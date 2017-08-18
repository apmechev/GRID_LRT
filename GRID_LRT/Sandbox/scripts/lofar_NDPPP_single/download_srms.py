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
        self.progress=0
        self.extracted=0
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
        elif "psnc" in self.srm:
            self.turl=self.srm.replace("srm://lta-head.lofar.psnc.pl:8443","gsiftp://door02.lofar.psnc.pl:2811")
        else:
            try:
                subprocess.Popen(["uberftp","-ls",self.srm])
            except:
                print "Can't gett size"
        if 'gsiftp' in self.srm: self.turl=self.srm
        ubersize=subprocess.Popen(["uberftp","-ls",self.turl],stdout=subprocess.PIPE)
        uber_result=ubersize.communicate()[0]
        try:
            self.size=uber_result.split()[4]
            self.filename=re.sub('_[a-z,1-9]{8}',"",uber_result.split()[8])
            self.filename=re.sub('.tar*','/',self.filename)
        except:
            try:
                s_size=subprocess.Popen(["srmls",self.srm],stdout=subprocess.PIPE)
                self.size=s_size.communicate()[0].split()[0]
            except:
                print "Can't get size"

    def getprogress(self):
        FNULL = open(os.devnull, 'w')
        if (time.time() - self.start_time) > 200*(float(self.size)/1000000000.) and (time.time() - self.start_time) > 1800 : 
            self.done=True
            self.kill_dl()
        try:
            os.kill(self.pid, 0)
        except OSError:
            self.done=True
            self.progress=1
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
                filename=os.path.abspath(curr_file) #temp filename to test
                if self.filename:
                    getdlsize=subprocess.Popen(["du","-s",self.filename],stdout=subprocess.PIPE,stderr=FNULL)
                else:
                    getdlsize=subprocess.Popen(["du","-s",filename],stdout=subprocess.PIPE,stderr=FNULL)
                self.filename=filename
                self.extracted=getdlsize.communicate()[0].split()[0]
            except:
                self.extracted=0
                if self.filename:
                    getdlsize=subprocess.Popen(["du","-s",self.filename],stdout=subprocess.PIPE,stderr=FNULL)
                    try:
                        self.extracted=getdlsize.communicate()[0].split()[0]
                    except:
                        pass
                if (time.time()-self.start_time) < 60 :
                    return 0.0
                
                self.stuck=True
                if (time.time()-self.start_time) > 200*(float(self.size)/1000000000.) and (time.time() - self.start_time) > 1800 :
                    self.kill_dl()
                    return 1
        self.progress=float(self.extracted)/float(float(self.size)/1000.)
        return self.progress


    def kill_dl(self):
        gettarpid=subprocess.Popen(["pgrep","-P",str(self.pid)],stdout=subprocess.PIPE)
        tarpids=gettarpid.communicate()[0].split()
        print "Attempting Delete of "+self.filename
        os.kill(self.pid,signal.SIGKILL)
        try:
            subprocess.Popen(['rm','-rf',self.filename])
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
            if os.path.exists(self.filename):
                self.done=True
                return
        try:
            os.kill(self.pid, 0)#relax this doesn't *really* kill anything :)
        except OSError:
            self.done=True
        if (time.time()-self.start_time)> 200*(float(self.size)/1000000000.) and (time.time() - self.start_time) > 1800 :
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
    print "download srms has caught "+str(len(srms))+" fiels"
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
            if (time.time()-x.start_time) > 200*(float(x.size)/1000000000.) and (not (x.done)) and ((time.time() - x.start_time) > 1800) :
                x.done=True
                x.kill_dl()
                print "killing process in last block"
        prog=[x.getprogress() for x in running]
        if len(glob.glob("GRID*"))==0:
            break
 

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
