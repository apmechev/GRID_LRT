import os
import sys
import glob
import shutil
import itertools 
import subprocess

class LRT(object):
    """
    The LRT class is created to be inherited and extended by different types of Lofar Reduction Tools
    (FAD_LRT, prefactor_LRT, killMS_LRT, factor_LRT, LGPPP_LRT, etc)
    It is designed to have options and features common to all LRTs and as a class, it holds instance
    variables in case the user needs to access the internals. 
    """
    def __init__(self):
        """ The initialization of the class makes most of the variables empty
            The user can pass them to parse_args (backwards compat, and makes easy to use with sys.args
        """
        self.srmfile=""
        self.workdir=os.environ["PWD"]
        self.resuberr=False
        self.OBSID=""
        self.sw_dir="/cvmfs/softdrive.nl/wjvriend/lofar_stack"
        self.sw_ver="2.16"
        self.jdl_file="remote.jdl"
        self.ignoreunstaged=False
        self.numpernode=1
        self.nostage=False

    def print_help(self):
        print ""
        print "You need to input the SRM file and the config/parset file"
        print "ex.  ./FAD_LRT.py [OPTIONS] srm_L229587.txt master_setup.cfg"
        print "optional flags ( -r, -j, -s, -noTS, -d, -v) come before srm and config file "
        print ""
        print "+=+=+=+= Default LRT Options +=+=+=+="
        print "(-r  or --resub-error-only)       - resubmit only error tokens "
        print "(-i  or --ignore-unstaged)        - If any files unstaged, it doesn't exit but continue "
        print "(-n  or --num-per-node)           - Splits SRMS to have a certain nuber on each node "
        print "(-j  or --jdl)                    - specify .jdl file to run  " 
        print "(-d  or --software-dir)           - path to custom LOFAR software dir "
        print "(-v  or --software-version)       - software version (subfolder of software-dir)"
        print "(-ns or --no-stage)               - do not stage the files if any NEARLINE (be kind to LTA)" 
        print "(-h  or --help)                   - prints this message (obv)"


    def parse_arguments(self,args):
        if ("-h" in args) or ("--help" in args):
            self.print_help()
            sys.exit()
        if ("srm" in args[-2]) and (".cfg" in args[-1] or ".parset" in args[-1]):
            self.srmfile=os.path.abspath(args[-2])
            if ".cfg" in args[-1]:
                self.cfgfile=os.path.abspath(args[-1])
            elif ".parset" in args[-1]:
                self.parsetfile=os.path.abspath(args[-1])
        elif ("srm" in args[-1]) and (".cfg" in args[-2] or ".parset" in args[-2]):
            self.srmfile=os.path.abspath(args[-1])
            if ".cfg" in args[-2]:
                self.cfgfile=os.path.abspath(args[-2])
            elif ".parset" in args[-2]:
                self.parsetfile=os.path.abspath(args[-2])

        if ("-r" in args[:-1] or ("--resub-error-only" in args[:-1])):
            print "\033[33mFlag set to resubmit only error tokens\033[0m"
            self.resuberr=True

        if ("-d" in args[:-1] or ("--software-dir" in args[:-1])):
            try:
                    idx=args.index("-d")
            except:
                    idx=args.index("--software-dir")
            print "Using Software dir=\033[33m"+args[idx+1]+"\033[0m"
            self.sw_dir=args[idx+1]

        if ("-v" in args[:-1] or ("--software-version" in args[:-1])):
            try:
                idxv=args.index("-v")
            except:
                idxv=args.index("--software-version")
            print "Using Software version=\033[33m"+args[idxv+1]+"\033[0m"
            self.sw_ver=args[idxv+1]

        if ("-i" in args[:-1] or ("--ignore-unstaged" in args[:-1])):
            print "Will continue even if files unstaged"
            self.ignoreunstaged=True

        if ("-ns" in args[:-1] or ("--no-stage" in args[:-1])):
            print "Will not attempt staging"
            self.nostage=True


        if ("-j" in args[:-1] or ("--jdl" in args[:-1])):
            try:
                idxv=args.index("-j")
            except:
                idxv=args.index("--jdl")
            print "Using jdl_file="+args[idxv+1]
            self.jdl_file=args[idxv+1] 



    def splitsrms(self,autoselect=-1):
        """The if autoselect is a positive integer, 
        this method doesn't wait for user interaction but chooses the nth srm file
        (starting from zero). Best used in fields to automate srm_files with [cal,targ] in the same srmfile
        """
        import re 
        OBSIDS=[]
        srmfiles=[]
        with open(self.srmfile,'r') as txtfile:
            lines=txtfile.readlines()
            for line in lines:
                obsid='L'+str(re.search("L(.+?)_",line).group(1))
                if not obsid in OBSIDS:
                    OBSIDS.append(obsid)
            print "Found "+str(len(OBSIDS))+" different OBSIDS. Splitting into files"

            for obsid in OBSIDS:
                print "What should I call the srmfile with OBSID ",obsid," (Default is srm_"+obsid+")"
                srmfile="srm_"+obsid
                from termios import tcflush, TCIOFLUSH
                if len(OBSIDS)>1:
                    tcflush(sys.stdin, TCIOFLUSH) #Flush input buffer to stop enter-spammers
                    userfile = raw_input().lower()
                    if userfile != "":
                        srmfile=userfile
                srmfiles.append(srmfile)
                with open(srmfile,'w') as file1:
                   [file1.write(x) for x in lines if obsid in x]

        if len(OBSIDS)>1:
            print "enter which file to process"
            for i in range(len(srmfiles)):
                print(str(i)+" "+srmfiles[i])
            if autoselect<0:
                userchoice = raw_input().lower()
            else:
                userchoice=autoselect
            if int(userchoice) in range(len(srmfiles)):
                userchoice=int(userchoice)
            else:
                sys.exit()
            self.srmfile=os.path.abspath(srmfiles[userchoice])
        with open(self.srmfile,'r') as f:
            line=f.readline()
            self.OBSID='L'+str(re.search("L(.+?)_",line).group(1))


        

    def setup_dirs(self):
        print ""
        print "You're running \033[33m SARA LRT1.5\033[0m, default"
        print ""
        #Check if the OBSID really is in the srmfile:
        found=False
        with open(self.srmfile,'rt') as f:
            for line in f:
                if self.OBSID in line:
                    found=True
                    print("Processing OBSID=\033[32m"+self.OBSID+"\033[0m")
                    break
            if not found:
                    print "\033[31mOBSID not found in SRM file!\033[0m"
                    sys.exit()
        sys.path.append('LRT/gsurl')
        import gsurl_v3
        try:
            for stuff in glob.glob('LRT/Tokens/datasets/'+self.OBSID+"/"):
                shutil.rmtree(stuff)
            for stuff in glob.glob('LRT/Staging/datasets/'+self.OBSID+"/"):
                shutil.rmtree(stuff)
            for oldstagefile in glob.glob("LRT/Staging/*files*"):
                os.remove(oldstagefile)
        except OSError:
            pass
        #creating files in [Tokens,Staging]/dataset/OBSID
        os.makedirs('LRT/Tokens/datasets/'+self.OBSID)
        os.makedirs('LRT/Staging/datasets/'+self.OBSID)
        gsurl_v3.main(self.srmfile,stride=self.numpernode)  #creates srmlist and subbandlist files
        shutil.copy("srmlist","LRT/Tokens/datasets/"+self.OBSID)
        shutil.copy("subbandlist","LRT/Tokens/datasets/"+self.OBSID)
        os.remove("srmlist")
        os.remove("subbandlist")
        gsurl_v3.main(self.srmfile)  #creates srmlist and subbandlist files
        shutil.copy("srmlist","LRT/Staging/datasets/"+self.OBSID)
        shutil.copy("subbandlist","LRT/Staging/datasets/"+self.OBSID)

        # fills PART of setup.cfg in [Tokens,Staging]/dataset/OBSID.
        # TODO:The user that inherits this process needs to extend this if
        # They later parse this file (as in FAD_LRT currently)
        for dir1 in ['Tokens','Staging']:
            with open("LRT/"+dir1+"/datasets/"+self.OBSID+"/setup.cfg","a") as cfgfile:
                cfgfile.write("[OBSERVATION]\n")
                cfgfile.write("OBSID           = "+self.OBSID+"\n")
                cfgfile.write("lofar_sw_dir    = "+self.sw_dir+"/"+self.sw_ver+'\n')
    

    def prepare_sandbox(self,sandboxdir="LRT/Application/sandbox"):
        import subprocess
        os.chdir(sandboxdir)
        sandboxname=os.path.basename(sandboxdir)        
        if "$" in self.sw_dir:
            testdir=os.environ[self.sw_dir[1:]]
        else:
            testdir=self.sw_dir
        if os.path.isdir(testdir) and os.path.isdir(testdir+"/"+self.sw_ver):
            pass
        else:
            print "directory "+testdir+"/"+self.sw_ver+" doesn't exist Exiting"
            sys.exit()
        os.chdir("../")
        
        subprocess.call(["tar","-cf", sandboxname+".tar",sandboxname+"/"])
        sandbox_base_dir="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox"
        subprocess.call(["uberftp", "-rm", sandbox_base_dir+"/sandbox_"+os.environ["PICAS_USR"]+"_"+self.OBSID+".tar"])
        subprocess.call(['globus-url-copy', "file:"+os.environ["PWD"]+"/LRT/Application/"+sandboxname+".tar",sandbox_base_dir+"/sandbox_"+os.environ["PICAS_USR"]+"_"+self.OBSID+".tar"])
        os.chdir(self.workdir)
        

    def fix_srms(self,path='srm:\/\/lofar-srm.fz-juelich.de:8443'):
        import re
        with open("LRT/Staging/"+self.OBSID+"_files","a") as Stagefile:
            with open("LRT/Staging/datasets/"+self.OBSID+"/srmlist",'r') as srms:
                for i,line in enumerate(srms):
                    line=re.sub("//pnfs","/pnfs",line)
                    if "poznan" in line:
                        line=re.sub("//lofar","/lofar",line)
                    Stagefile.write(re.sub(path,'',line.split()[0])+'\n')
        Stagefile.close()


    def check_state_and_stage(self):
        file1=open("LRT/Staging/datasets/"+self.OBSID+"/srmlist",'r').read()
        if "fz-juelich.de" in file1:
            self.fix_srms('srm:\/\/lofar-srm.fz-juelich.de:8443')
        elif "srm.grid.sara.nl" in  file1:
            self.fix_srms('srm:\/\/srm.grid.sara.nl:8443')
        elif "lofar.psnc.pl" in file1 :
            self.fix_srms('srm:\/\/lta-head.lofar.psnc.pl:8443')
        os.chdir(self.workdir+"/LRT/Staging/")
        for oldfile in glob.glob("files"):
            os.remove(oldfile)
        sys.path.append(os.path.abspath("."))
        shutil.copy(self.OBSID+"_files","files")
        import state_all
        import stage_all
        self.locs=state_all.main('files')
        self.unstaged=[item for sublist in self.locs for item in sublist].count('NEARLINE')/(float(len(self.locs)))
        if self.unstaged<0.01:
            pass
        else:
            if not self.nostage:
                stage_all.main('files')
        os.chdir(self.workdir)

    def submit_to_picas(self,token_type="token",keys={},attfile=""):
        sys.path.append(os.getcwd()+"/LRT/Tokens")
        os.chdir(self.workdir+"/LRT/Tokens")
        try:
            print "Your picas user is "+os.environ["PICAS_USR"]+" and the DB is "+os.environ["PICAS_DB"]
        except KeyError:
            print "\033[31m You haven't set $PICAS_USR or $PICAS_DB or $PICAS_USR_PWD! \n\n Exiting\033[0m"
            sys.exit()
        import Token
        th=Token.Token_Handler(uname=os.environ["PICAS_USR"],pwd=os.environ["PICAS_USR_PWD"],dbn=os.environ["PICAS_DB"],t_type=token_type)
        th.add_view("todo",'doc.lock == 0 && doc.done == 0')
        th.add_view("locked",'doc.lock > 0 && doc.done == 0')
        th.add_view("done",'doc.lock > 0 && doc.done > 0 && doc.output == 0')
        th.add_view("error",'doc.lock > 0 && doc.done > 0 && doc.output > 0')
        th.add_overview_view()

        if self.resuberr:
            th.reset_tokens(view_name=self.OBSID)
        else:
            th.add_view(v_name=self.OBSID,cond='doc.OBSID == "%s" '%(self.OBSID))
            th.delete_tokens(view_name=self.OBSID)
            num_token=0
            for line in open("datasets/"+self.OBSID+"/subbandlist",'rb'):
                if len(self.parsetfile )>5:
                    attachment=[open(attfile,'r'),os.path.basename(attfile)]
                    default_keys={"num_per_node":self.numpernode,"lofar_sw_dir":self.sw_dir+"/"+self.sw_ver,"OBSID":self.OBSID,"start_SB":num_token*self.numpernode}
                    th.create_token(keys=dict(itertools.chain(keys.iteritems(), default_keys.iteritems())),append=self.OBSID+"_"+line.rstrip(),attach=attachment)
                    num_token+=1

        os.chdir(self.workdir)

        os.remove('srmlist')
        os.remove('subbandlist')

    def start_jdl(self):
        os.chdir(self.workdir+"/LRT/Application")
        #TODO: Change avg_dmx's number of jobs to number of subbands
        dmx_jdl=self.jdl_file
        shutil.copy(dmx_jdl,'avg_dmx_with_variables.jdl')
        self.replace_in_file(dmx_jdl,'$PICAS_DB $PICAS_USR $PICAS_USR_PWD', os.environ["PICAS_DB"]+" "+os.environ["PICAS_USR"]+" "+os.environ["PICAS_USR_PWD"])

        num_lines = sum(1 for line in open(self.srmfile))
        numprocess = num_lines/self.numpernode+[0,1][num_lines%self.numpernode>0]
        print numprocess
        self.replace_in_file(dmx_jdl,"Parameters=50","Parameters="+str(numprocess))

        subprocess.call(['glite-wms-job-submit','-d',os.environ["USER"],'-o','jobIDs'+self.OBSID,dmx_jdl])
        self.glite_job=open('jobIDs'+self.OBSID).readlines()[-1]
        shutil.move('avg_dmx_with_variables.jdl',dmx_jdl)
        os.chdir(self.workdir)


    def replace_in_file(self,filename="",istring="",ostring=""):
            filedata=None
            with open(filename,'r') as file:
                filedata = file.read()
            filedata = filedata.replace(istring,ostring)
            os.remove(filename)
            with open(filename,'w') as file:
                file.write(filedata)





