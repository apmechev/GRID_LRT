#!/bin/python
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2014
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

#******************************************************************************
#
#
# Who       When        What
# --------  ----------  -------------------------------------------------------
# cwu      31/Mar/2014  Created
#

"""
trace cpu and memory usage
info from /proc
"""
from collections import namedtuple
from optparse import OptionParser
import os, sys, time, commands, gc, signal
import cPickle as pickle



# /proc/[pid]/stat layout
# Specs - https://www.kernel.org/doc/Documentation/filesystems/proc.txt
proc_pid_stat='''
pid           process id
  tcomm         filename of the executable
  state         state (R is running, S is sleeping, D is sleeping uninterruptible, Z is zombie, T is traced or stopped)
  ppid          process id of the parent process
  pgrp          pgrp of the process
  sid           session id
  tty_nr        tty the process uses
  tty_pgrp      pgrp of the tty
  flags         task flags
  min_flt       number of minor faults
  cmin_flt      number of minor faults with child's
  maj_flt       number of major faults
  cmaj_flt      number of major faults with child's
  utime         user mode jiffies
  stime         kernel mode jiffies
  cutime        user mode jiffies with child's
  cstime        kernel mode jiffies with child's
  priority      priority level
  nice          nice level
  num_threads   number of threads
  it_real_value (obsolete, always 0)
  start_time    time the process started after system boot
  vsize         virtual memory size
  rss           resident set memory size
  rsslim        current limit in bytes on the rss
  start_code    address above which program text can run
  end_code      address below which program text can run
  start_stack   address of the start of the main process stack
  esp           current value of ESP
  eip           current value of EIP
  pending       bitmap of pending signals
  blocked       bitmap of blocked signals
  sigign        bitmap of ignored signals
  sigcatch      bitmap of caught signals
  wchan         address where process went to sleep
  plh0          (place holder)
  plh1          (place holder)
  exit_signal   signal to send to parent thread on exit
  task_cpu      which CPU the task is scheduled on
  rt_priority   realtime priority
  policy        scheduling policy (man sched_setscheduler)
  blkio_ticks   time spent waiting for block IO
  gtime         guest time of the task in jiffies
  cgtime        guest time of the task children in jiffies
  start_data    address above which program data+bss is placed
  end_data      address below which program data+bss is placed
  start_brk     address above which program heap can be expanded with brk()
  arg_start     address above which program command line is placed
  arg_end       address below which program command line is placed
  env_start     address above which program environment is placed
  env_end       address below which program environment is placed
  exit_code     the thread's exit_code in the form reported by the waitpid system call
'''
proc_pid_stat_dict=dict([(x.split()[0],i) for i,x in enumerate(proc_pid_stat.splitlines()[1:])])

# Lookup indices of metrics
I_UT  = proc_pid_stat_dict['utime']
I_ST  = proc_pid_stat_dict['stime']
I_CUT = proc_pid_stat_dict['cutime']
I_CST = proc_pid_stat_dict['cstime']
I_VM  = proc_pid_stat_dict['vsize']
I_RSS = proc_pid_stat_dict['rss']


# Stat file locations
FSTAT = '/proc/stat'
FMEMINFO = '/proc/meminfo'

"""
ts:        time stamp
u:         user cpu of this process
k:         kernel cpu of this process
cu:        user cpu of child process
ck:        kernel cpu of child process
all:       cpu of all processes
vm:        virtual memory size
rss:       resident set size (memory portion)
"""
pstat = namedtuple('pstat', 'ts u k cu ck vm rss sys_cpu sys_mem')


def execCmd(cmd, failonerror = True):
    re = commands.getstatusoutput(cmd)
    if (re[0] != 0):
        errMsg = 'Fail to execute command: "%s". Exception: %s' % (cmd, re[1])
        if (failonerror):
            raise Exception(errMsg)
        else:
            print errMsg
    return re

def getSysPageSize():
    cmd = "getconf PAGESIZE"
    re = execCmd(cmd)
    return int(re[1])

def printSample(splList):
    """
    This is for testing
    
    splList    a list of samples (list)
    """
    from prettytable import PrettyTable
    tbl = PrettyTable(["Time stamp", "User CPU", "Kernel CPU", "U-Child CPU", 
                       "K-Child CPU", "VM", "RSS", "System CPU", "System Mem"])
    tbl.padding_width = 1 # One space between column edges and contents (default)
    
    for p in splList:
        tbl.add_row([p.ts, p.u, p.k, p.cu, p.ck, p.vm, p.rss, p.sys_cpu, p.sys_mem])
    
    print tbl

def computeUsage(splList, printList = False, saveToFile = None):
    """
    Convert from sample to CPU/memory usage
    
    splList    sample list (a list of samples (pstat))
    Return:    a list of statistics (tuples[timestamp, user_cpu, kernel_cpu, vm, rss, sys_cpu, sys_mem])
    """
    pgsz = getSysPageSize()
    reList = [] # 
    leng = len(splList)
    if (leng < 2):
        raise Exception("sample size is too small")
    # refer to http://stackoverflow.com/questions/4189123/python-how-to-get-number-of-mili-seconds-per-jiffy
    # refer to http://stackoverflow.com/questions/16726779/total-cpu-usage-of-an-application-from-proc-pid-stat
    Hertz = os.sysconf(os.sysconf_names['SC_CLK_TCK'])
    gc.disable()

    for i in range(leng - 1):
        sp1 = splList[i]
        sp2 = splList[i + 1]

        tcpu1 = sp1.u + sp1.k + sp1.cu + sp1.ck
        tcpu2 = sp2.u + sp2.k + sp2.cu + sp2.ck
        kcpu1 = sp1.k + sp1.ck
        kcpu2 = sp2.k + sp2.ck

        walltime = 1 # 1 seconds
        tu = int(100.0 * (tcpu2 - tcpu1) / Hertz / walltime)
        ku = int(100.0 * (kcpu2 - tcpu1) / Hertz / walltime)
        allcpu = int(100.0 * (sp2.sys_cpu - sp1.sys_cpu) / Hertz / walltime)
        allmem = sp2.sys_mem
        
        itm = (sp2.ts, tu, ku, sp2.vm, pgsz * sp2.rss, allcpu, allmem)
        reList.append(itm)

    gc.enable()
    
    if (printList):
        from prettytable import PrettyTable
        tbl = PrettyTable(["Time stamp", "Total CPU %", "Kernel CPU %", "VM", "RSS", "System  CPU %", "System Mem"])
        tbl.padding_width = 1
        
        for p in reList:
            tbl.add_row([p[0], p[1], p[2], p[3], p[4], p[5], p[6]])
        
        print tbl
    
    if (saveToFile):
        print 'Saving CPU statistics to file %s ...' % saveToFile
        try:
            output = open(saveToFile, 'wb')
            stt = time.time()
            pickle.dump(reList, output)
            output.close()
            print 'Time for saving CPU statistics: %.2f' % (time.time() - stt)
        except Exception, e:
            ex = str(e)
            print 'Fail to save CPU statistics to file %s: %s' % (saveToFile, ex)
    
    return reList

def processSample(raw_sample):
    # Sample for specific pid
    pa_line = raw_sample[0]
    pa = pa_line.split()

    # System wide cpu sample
    cpu_line = raw_sample[1]
    cpu_used = int(cpu_line.split()[1])

    # System wide mem sample
    mem_lines = raw_sample[2]
    mem_values = [int(line.split()[1]) for line in mem_lines]
    mem_total = mem_values[0]
    mem_avail = mem_values[2]
    mem_used = (mem_total - mem_avail)

    # Timestamp
    ts = raw_sample[3]
    
    ret = pstat(ts, int(pa[I_UT]), int(pa[I_ST]), int(pa[I_CUT]), int(pa[I_CST]), 
                int(pa[I_VM]), int(pa[I_RSS]), cpu_used, mem_used)
    
    return ret

def collectSample(pid):
    """
    retrieve current usage sample
    This will be called every N seconds
    
    pid:        process id (int) 
    
    Return:    an instance of the pstat namedtuple 
    """
    # Timestamp
    ts = time.time()

    # Read system wide samples
    fstat_line = open(FSTAT).readline()
    fmeminfo_lines = open(FMEMINFO).readlines()

    # Read sample for specific pid
    fstat_line_pid = open("/proc/%d/stat" % (pid)).readline()

    return (fstat_line_pid, fstat_line, fmeminfo_lines, ts)

ps = []

def exitHandler(signum, frame):
    """
    ps:    raw samples
    """
    print "Receiving signal ", signum
    
    print "Processing samples ..."
    pas = [processSample(x) for x in ps]
    print "Compute CPU statistics ..."
    computeUsage(pas, printList = False, saveToFile = options.save_cpu_file)
    exit(0)

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-p", "--pid", action="store", type="int", dest="pid")
    parser.add_option("-o", "--outputfile", action="store", dest="save_cpu_file",
                      type = "string", default = "", help = "Save CPU stats to the file")
    
    (options, args) = parser.parse_args()
    if (None == options.pid or None == options.save_cpu_file):
        parser.print_help()
        sys.exit(1)
    
    fname = '/proc/%d/stat' % options.pid
    if (not os.path.exists(fname)):
        print "Process with pid %d is not running!" % options.pid
        sys.exit(1)
    
    signal.signal(signal.SIGTERM, exitHandler)
    signal.signal(signal.SIGINT, exitHandler)
    
    while (1):
        sst = time.time()
        try:
            sp = collectSample(options.pid)
        except IOError, ioe:
            print ("Error occured %s" % str(ioe))
            exitHandler(15, None) # the process has terminated, so finish CPU monitoring...
            
        ps.append(sp)
        time.sleep(1 - (time.time() - sst))
