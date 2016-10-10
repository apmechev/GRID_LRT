from class_default_LRT import LRT


class FAD_LRT(LRT):
    def __init__(self):
        LRT.__init__(self)
        self.jdl_file="remote.jdl"
        self.TSplit=True
        self.numpernode=1

    def print_help(self):
        LRT.print_help(self)
        print "+=+=+=+=+=+= FAD LRT Options +=+=+=+=+=+="
        print "(-noTS or --no-time-splitting)   - turn off Time Splitting "
        print "(-s or --script)                 - custom script to launch "


    def parse_arguments(self,args): 
        if ("-n" in args[:-2] or ("--number-per-node" in args[:-2])):
                try:
                        idxv=args.index("-n")
                except:
                        idxv=args.index("--number-per-node")
                print "Sending "+args[idxv+1]+" Subbands per node"
                self.numpernode=int(args[idxv+1])
        if ("-noTS" in args[:-2] or ("--no-time-splitting" in args[:-2])):
                print "\033[33mTurning Off Timesplitting\033[0m"
                self.TSplit=False
        if ("-s" in args[:-2] or ("--script" in args[:-2])):
                try:
                        idxv=args.index("-s")
                except:
                        idxv=args.index("--script")
                print "Using Custom script="+args[idxv+1]
                self.customscript=os.path.abspath(args[idxv+1])

        LRT.parse_arguments(self,args)
    
    def split_srms(self):
        LRT.split_srms(self)

    def setup_dirs(self):
        LRT.setup_dirs(self) 
    def prepare_sandbox(self,sandboxdir=""):
        if not sandboxdir:
            #sandboxdir=self.workdir+"/LRT/Application/sandbox" 
            sandboxdir=self.workdir+"/LRT/Application/lgppp-sandbox" 
            print "Prepare sandbox: ", sandboxdir
        LRT.prepare_sandbox(self,sandboxdir)

    def check_state_and_stage(self):
        LRT.check_state_and_stage(self)

    def submit_to_picas(self,pref_type="",add_keys={}):
        #LRT.submit_to_picas(self,token_type="FAD"+pref_type,keys=add_keys,attfile=self.parsetfile)
        LRT.submit_to_picas(self,token_type="token"+pref_type,keys=add_keys,attfile=self.parsetfile)

    def start_jdl(self):
        LRT.start_jdl(self)
