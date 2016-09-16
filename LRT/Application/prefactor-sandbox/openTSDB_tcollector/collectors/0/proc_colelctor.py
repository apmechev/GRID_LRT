#!/usr/bin/env python
# NTP Offset stats
# charlesrg AT gmail.com
#
# procstat.py
#

import os
import subprocess
import sys
import time
import errno

import pdb
from collectors.lib import utils

class flushfile(file):
    def __init__(self, f):
        self.f = f
    def write(self, x):
        self.f.write(x)
        self.f.flush()



try:
  from collectors.etc import proc_conf
except ImportError:
  proc_conf = None


DEFAULT_COLLECTION_INTERVAL=10

def getPIDs(st):
    ''' This searches the current user's running processes for a string
        which allows to trace scripts by searching the srcipt name whereas
        pidof will only catch the interpreter name. Uses ps.
    '''
    USER=os.environ["USER"]
    pl = subprocess.Popen(['ps', '-u',USER,'-o','pid cmd'], stdout=subprocess.PIPE).communicate()[0]
    ##TODO:Wrap above in trycatch
    pids=[]

    for i in pl.split('\n'):
        if st in i:
            pids.append(i.lstrip().split(' ')[0])

    return pids


def main(proc_names=[]):
    """main loop waiting for process"""

    collection_interval=DEFAULT_COLLECTION_INTERVAL
    if(proc_conf):
        config = proc_conf.get_config()
        collection_interval=config['collection_interval']
        proc_names.append(config['proclist'])#Appends!
    sys.stderr.write(str(len(proc_names)))
    utils.drop_privileges()
    
    tmp=proc_names[0]
    proc_names=[]
    proc_names=tmp

    no_trace=dict(zip(proc_names[:],["" for x in range(len(proc_names))]))
        #zip each procname with "" and make dict
    for pname in proc_names:
        no_trace[pname]=getPIDs(pname) #This list holds all old processes as well as ones traced

    procs=[] #holds process objects for stdout read
    while True:
        ts = int(time.time())
        find_pids=dict(zip(proc_names[:],[[] for x in range(len(proc_names))]))
        for pname in proc_names:
            p_tmp=getPIDs(pname) #for all matching pids, trace ones not in notrace, add them
            for pid in p_tmp:	
                if pid not in no_trace[pname]: 
                    try:
                        proc_trace=subprocess.Popen(["/cvmfs/softdrive.nl/apmechev/tools/proc_stat/proc_stat", pid],stdout=subprocess.PIPE)
                        #proc_trace=subprocess.Popen(["/home/apmechev/procsamp/bin/Debug/procfs-sampler", pid],stdout=subprocess.PIPE)
			#pdb.set_trace()
			#ex("../../procfsamp "+pid+" &")
                        no_trace[pname].append(pid)
                        procs.append(proc_trace)
                    except OSError:
                           sys.stderr.write("Launch error a@ proc Sampler")
	stdout=[]	
        for p in procs:
#	   pdb.set_trace()
           while True:
               line = p.stdout.readline()
               stdout.append(line)
               print line,
               if line == '' and p.poll() != None:
                   sys.stdout.flush()
                   break
	sys.stdout.flush()
        time.sleep(collection_interval)

if __name__ == "__main__":
    main()
