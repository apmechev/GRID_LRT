#/usr/bin/env python

import signal
import subprocess
import re
import os
import time
import pdb
import sys
import glob

class srm_getter:
    def __init__(self,srm):
        self.done=False
        self.stuck=False
        self.restart=False
        if len(srm.split())>1:
            self.srm = srm.split()[0]
        else:
            self.srm=srm
       
    def start(self):
        self.proc=subprocess.Popen(['./prefactor/bin/getfiles.sh',self.srm])
        self.pid=self.proc.pid
        self.start_time=time.time()
        print "PID" +str(self.pid)
        if "lofar-srm.fz-juelich.de" in self.srm:
            self.turl=self.srm.replace("srm://lofar-srm.fz-juelich.de:8443","gsiftp://dcachepool12.fz-juelich.de:2811")
        elif "srm.grid.sara.nl" in self.srm:
            self.turl=self.srm.replace("srm://srm.grid.sara.nl:8443","gsiftp://gridftp.grid.sara.nl:2811")
        else:
            try:
                subprocess.Popen(["uberftp","-ls",self.srm])
            except:
                pass
        ubersize=subprocess.Popen(["uberftp","-ls",self.turl],stdout=subprocess.PIPE)
        uber_result=ubersize.communicate()[0]
        self.size=uber_result.split()[4]
        self.filename=re.sub('_[a-z,1-9]{8}',"",uber_result.split()[8])
        self.filename=re.sub('.tar*','/',self.filename)

    def getprogress(self):
        FNULL = open(os.devnull, 'w')
        if (time.time() - self.start_time) > 900: 
            self.done=True
            self.kill_dl()
        if self.done: return 
        try:
            getdlsize=subprocess.Popen(["du","-s",self.filename],stdout=subprocess.PIPE,stderr=FNULL)
            self.extracted=getdlsize.communicate()[0].split()[0]
        except: #not the easy way to do this:get tar pid, find fd and return size of fd parent (TODO:needs to ~match filename)
            time.sleep(3)
            gettarpid=subprocess.Popen(["pgrep","-P",str(self.pid)],stdout=subprocess.PIPE)
            try:
                tarpids=min(gettarpid.communicate()[0].split())
                curr_file=os.readlink("/proc/"+tarpids+"/fd/4")
                #filename=os.path.abspath(os.path.join(curr_file, os.pardir))
                filename=os.path.abspath(os.path.dirname(curr_file)) #temp filename to test
                if self.filename:
                    getdlsize=subprocess.Popen(["du","-s",self.filename],stdout=subprocess.PIPE,stderr=FNULL)
                else:
                    getdlsize=subprocess.Popen(["du","-s",filename],stdout=subprocess.PIPE,stderr=FNULL)
                self.filename=filename
                self.extracted=getdlsize.communicate()[0].split()[0]
            except:
                self.extracted=0.0
                if (time.time()-self.start_time) < 60 :
                    return 0.0
                
                self.stuck=True
                if (time.time()-self.start_time) > 600 :
                    self.kill_dl()
                    return 1
        self.progress=float(self.extracted)/float(float(self.size)/1000.)
        return self.progress


    def kill_dl(self):
        gettarpid=subprocess.Popen(["pgrep","-P",str(self.pid)],stdout=subprocess.PIPE)
        tarpids=gettarpid.communicate()[0].split()
        os.kill(self.pid,signal.SIGKILL)
        try:
            os.rmfile(self.filename)
        except:
            pass
        for tarpid in tarpids:
            try:
                os.kill(int(tarpid),signal.SIGKILL)
            except:
                pass
        self.progress=1
        self.restart=True
        self.done=True


    def isdone(self):
        try:
            for line in open("/proc/%d/status" % self.pid).readlines():
                if line.startswith("State:"):
                    if line.split(":",1)[1].strip().split(' ')[0]=="Z": #Checks if process is Zombie
                        self.done=True
                        self.progress=1
                        return self.done
        except:
            pass
        try:
            os.kill(self.pid, 0)#relax this doesn't *really* kill anything :)
        except OSError:
            self.done=True
        if (time.time()-self.start_time)>900:
                self.done=True
                self.kill_dl()
        else:
                self.done=False
        return self.done

def main(srmfile,start=0,end=-1,step=10):
    '''
        Usage:  download_srms.py srmfile.txt (will down all subbands, 10 at a time from srmfile.txt)
                download_srms.py srmfile.txt 10 15 (will download lines 10 up to and NOT INCLUDING 15 *so 10->14 from srmfile.txt)
                download_srms.py srmfile.txt 0 200 20 (will download 20 at a time (you risk overloading the server cowboy!!))
                download_srms.py srmfile.txt 20 (same as above except downloads all srms)
    '''
    srms=[]
    with open(srmfile,'r') as f:
        for line in f:
            srms.append(line)
    if end==-1:
        srms=srms[start:]
    else:
        srms=srms[start:end]
    running=[]
    step=[step,end-start][step>(end-start) and (end-start)>0]
    for i in range(0,step): #if less than 10 items, len(running) shorter
        srm_tmp=srms[0]
        s=srm_getter(srm_tmp)
        running.append(s)
        running[-1].start()
        del srms[0]

    done=[x.isdone() for x in running]
    while len(srms)>0 :
        time.sleep(5) 
        prog=[x.getprogress() for x in running]
        done=[x.isdone() for x in running]
#        done=[x.done for x in running]
        if any(done):# if any of the items are finished
            idx=[i for i in range(step) if done[i]]
            for restart in idx:
                try:
                    srm_tmp=srms[0]
                    s=srm_getter(srm_tmp)
                    running[restart]=s
                    running[restart].start()
                    del srms[0]
                except IndexError:
                    pass
    while not all([x.done for x in running]):
        time.sleep(3)
        for x in running:
            if (time.time()-x.start_time) > 900 and not (x.done):
                x.done=True
                x.kill_dl()
        prog=[x.getprogress() for x in running]
    for f in glob.glob("GRID*tar"):
        os.remove(f)
    print [x.isdone() for x in running]
    return

if __name__ == "__main__":
    argv = sys.argv
    if len(argv)==2:
        main(argv[1])
    elif len(argv)==3:
        main(argv[1],step=int(argv[2]))
    elif len(argv)==4:
        main(argv[1],start=int(argv[2]),end=int(argv[3]))
