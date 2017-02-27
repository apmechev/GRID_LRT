import os
import sys
import glob
import shutil
import itertools 
import subprocess
import yaml

from GRID_LRT import srmlist
import GRID_LRT.sandbox as sandbox
import GRID_LRT.Token as Token


import pdb
class LRT(object):
    """
    The LRT class is created to be inherited and extended by different types of Lofar Reduction Tools
    (FAD_LRT, prefactor_LRT, killMS_LRT, factor_LRT, LGPPP_LRT, fields_LRT etc)
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
        '''Parses the arguments given to the program (or class) TODO: merge in init?
            It updates the instance variables accordingly
        '''
        print ""
        print "You're running \033[33m SARA LRT1.5\033[0m, default"
        print ""

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
        ##TODO: Put this in the srmObject
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
        '''This now exists for legacy support, it's all done in 
            check_state_and_stage()
        '''
        self.prepare_srms()


    def prepare_srms(self):
        '''This now exists for legacy support, it's all done in 
            check_state_and_stage()
        '''
        print ""
        print "You're running \033[33m SARA LRT1.5\033[0m, default"
        print ""
        
        self.Srm_obj=srmlist.Srm_manager(OBSID=self.OBSID,stride=self.numpernode)
        self.Srm_obj.file_load(self.srmfile)
        self.srms=self.Srm_obj.srms

    def prepare_sbx_from_config(self,sbxconfig,tokconfig):

        s=sandbox.Sandbox()
        s.parseconfig(sbxconfig)
        s.create_SBX_folder()
        s.enter_SBX_folder()
        s.load_git_scripts()
        s.copy_base_scripts()
        s.check_token(tokconfig)
        s.zip_SBX()
        s.upload_SBX()
        s.cleanup()
 

    def prepare_sandbox(self,sandboxdir="LRT/Application/sandbox"):
        '''Each job is contained in a sandbox and this function creates a
            sandbox and uploads it to the sanboxstorage
        '''
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
        

    def check_state_and_stage(self):
        '''The srmlist object also allows to stage and or check state
        '''
        ##TODO: Allow user to decide when to check and when to stage? 
        if not hasattr(self, 'Srm_obj'):
           self.prepare_srms()
        self.locs=self.Srm_obj.state()
        self.unstaged=[item for sublist in self.locs for item in sublist].count('NEARLINE')/(float(len(self.locs)))
        if self.unstaged<0.01:
            pass
        else:
            if not self.nostage:
                self.Srm_obj.stage()


    def submit_to_picas(self,token_type="token",keys={},attfile=""):
        '''Creates tokens and views in the PiCaS token pool or resubmits error tokens
        '''
        ##TODO: Refactor
        if not hasattr(self, 'Srm_obj'):
           self.prepare_srms()
        try:
            print "Your picas user is "+os.environ["PICAS_USR"]+" and the DB is "+os.environ["PICAS_DB"]
        except KeyError:
            print "\033[31m You haven't set $PICAS_USR or $PICAS_DB or $PICAS_USR_PWD! \n\n Exiting\033[0m"
            sys.exit()

        default_keys=yaml.load(open('config/tokens/pref_cal1_token.cfg','rb'))
        _=default_keys.pop('_attachments')
        self.t_type=token_type
        th=Token.Token_Handler(uname=os.environ["PICAS_USR"],pwd=os.environ["PICAS_USR_PWD"],dbn=os.environ["PICAS_DB"],t_type=token_type)
        th.add_view("todo",'doc.lock == 0 && doc.done == 0')
        th.add_view("locked",'doc.lock > 0 && doc.status !="done"&& doc.status !="error" && doc.status !="downloading" ')
        th.add_view("done",'doc.status == "done" ')
        th.add_view("error",'doc.status == "error" ')
        th.add_overview_view()
        #TODO: make token_holder object to store a LRT's tokens or just list?

        self.tokens=[]
        if keys['pipeline']=='pref_targ2':
            abnlist=self.Srm_obj.make_abndict_from_tokens(token_type)
            if self.resuberr:
                th.reset_tokens(view_name='error')
            for ABN in abnlist:
                th.delete_tokens(view_name='locked')
                attachment=[open(attfile,'r'),os.path.basename(attfile)] 
                token=th.create_token(keys=dict(itertools.chain(keys.iteritems(), 
                                      default_keys.iteritems())),
                                      append=self.OBSID+"_ABN"+str("%03d" % ABN),
                                      attach=attachment)
                with open('temp_abn','w') as tmp_abn_file:
                    for i in abnlist[ABN]:
                        tmp_abn_file.write("%s\n" % i)
                with open('temp_abn','r') as tmp_abn_file:
                    th.add_attachment(token,tmp_abn_file,"srm.txt")
                os.remove('temp_abn')
                self.tokens.append(token)


        ##TODO: Use a dictionary for EVERY token (download srm.txt in pilot.py)
        if keys['pipeline']!='pref_targ2':
            srmlist=self.Srm_obj.make_sbndict_from_file(self.srmfile) 
            if self.resuberr:
                th.reset_tokens(view_name='error')
            else:
                th.add_view(v_name=self.OBSID,cond='doc.OBSID == "%s" '%(self.OBSID))
                th.delete_tokens(view_name=self.OBSID)
                num_token=0 #used to stride the start_SB
                for SRM in srmlist:
                    attachment=[open(attfile,'r'),os.path.basename(attfile)]
                    token=th.create_token(keys=dict(itertools.chain(keys.iteritems(), 
                                          default_keys.iteritems())),
                                          append=self.OBSID+"_SB"+str("%03d" % int(SRM) ),
                                          attach=attachment)
                    with open('temp_abn','w') as tmp_abn_file:
                        for i in srmlist[SRM]:
                            tmp_abn_file.write("%s\n" % i)
                    with open('temp_abn','r') as tmp_abn_file:
                        th.add_attachment(token,tmp_abn_file,"srm.txt")
                    os.remove('temp_abn')
                    self.tokens.append(token)


    def start_jdl(self,num_jobs=None):
        '''Starts the jdl (IE it submits the job for processing)
        '''
        if self.resuberr: #return if resubmitting TODO: Check if any jdls are running, if so don't return
            return
        os.chdir(self.workdir+"/GRID_LRT/Application")
        #TODO: Change avg_dmx's number of jobs to number of subbands
        dmx_jdl=self.jdl_file
        shutil.copy(dmx_jdl,'avg_dmx_with_variables.jdl')
        self.replace_in_file(dmx_jdl,'$PICAS_DB $PICAS_USR $PICAS_USR_PWD', os.environ["PICAS_DB"]+" "+os.environ["PICAS_USR"]+" "+os.environ["PICAS_USR_PWD"]+" "+self.t_type)
        print "including "+self.t_type
        if num_jobs:
            numjobs =num_jobs
        else:
            num_lines = sum(1 for line in open(self.srmfile))
            numjobs = num_lines/self.numpernode+[0,1][num_lines%self.numpernode>0]
        print numjobs
        self.replace_in_file(dmx_jdl,"Parameters=1","Parameters="+str(numjobs))

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
