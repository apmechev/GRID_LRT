from  class_default_LRT import LRT
import os,sys,subprocess

class pref_LRT(LRT):
    def __init__(self):
        LRT.__init__(self)
        self.jdl_file="remote-prefactor.jdl"
        self.numpernode=10
        self.nostage=True

    def print_help(self):
        LRT.print_help(self)
        print "+=+=+=+=+ Prefactor LRT Options +=+=+=+=+="
        print "(-fs or --force-stage)                   - Force Staging of Files"

    def parse_arguments(self,args): 
        if ("-n" in args[:-2] or ("--number-per-node" in args[:-2])):
                try:
                        idxv=args.index("-n")
                except:
                        idxv=args.index("--number-per-node")
                print "Sending "+args[idxv+1]+" Subbands per node"
                self.numpernode=int(args[idxv+1])
        if ("-fs" in args[:-2] or ("--force-stage" in args[:-2])):
            self.nostage=False
        LRT.parse_arguments(self,args)
    
    def split_srms(self):
        LRT.split_srms(self)

    def setup_dirs(self):
        LRT.setup_dirs(self) 


    def prepare_sandbox(self,sandboxdir=None): 
        if not sandboxdir:
            sandboxdir=self.workdir+"/LRT/Application/prefactor-sandbox" 
        os.chdir(sandboxdir)
        try:
            os.remove("prefactor.tar")
            os.remove("prefactor/*.parset")
        except OSError:
            pass
        subprocess.call(["tar","-cf", "prefactor.tar","prefactor/"])
        os.chdir(self.workdir)

        LRT.prepare_sandbox(self,sandboxdir)

    def check_state_and_stage(self):
        if "Initial" in self.parsetfile:
            print "nothing to stage with Initial_subtract parset"
            return
        LRT.check_state_and_stage(self)
        if self.nostage:
            print "The files were not staged, but using -fs or --force-stage will stage them for you"
        for sublist in self.locs:
            if "NEARLINE" in sublist:
                if self.ignoreunstaged:
                    print " \033[31m Continuing although there are unstaged files\033[0m"
                    break
                print "\033[31m+=+=+=+=+=+=+=+=+=+=+=+=+=+="
                print "The srms are not ONLINE yet, use -fs or --force-stage to stage them." 
                print "I'll exit so the tokens don't crash. Re-run in a few (or tens of) minutes OR re-run with -i or --ignore-unstaged"
                perc_left=[item for sublist in self.locs for item in sublist].count('NEARLINE')/(float(len(self.locs)))
                print str(perc_left*100)+"%  left unstaged"
                print "+=+=+=+=+=++=+=+=+=+=+=+=+=\033[0m" 
                sys.exit()

    def submit_to_picas(self,pref_type="",add_keys={}):
        LRT.submit_to_picas(self,token_type="pref"+pref_type,keys=add_keys,attfile=self.parsetfile)

    def start_jdl(self):
        LRT.start_jdl(self)
