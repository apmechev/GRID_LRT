from  class_default_LRT import LRT


class pref_LRT(LRT):
    def __init__(self):
        LRT.__init__(self)
        self.jdl_file="remote-prefactor.jdl"

    def parse_arguments(self,args): 
        if ("-n" in args[:-2] or ("--number-per-node" in args[:-2])):
                try:
                        idxv=args.index("-n")
                except:
                        idxv=args.index("--number-per-node")
                print "Sending "+args[idxv+1]+" Subbands per node"
                self.numpernode=int(args[idxv+1])
        LRT.parse_arguments(self,args)
    
    def split_srms(self):
        LRT.split_srms(self)

    def setup_dirs(self):
        LRT.setup_dirs(self) 
    def prepare_sandbox(self,sandboxdir=""):
        if not sandboxdir:
            sandboxdir=self.workdir+"/LRT/Application/prefactor-sandbox" 
        LRT.prepare_sandbox(self,sandboxdir)

    def check_state_and_stage(self):
        LRT.check_state_and_stage(self)

    def submit_to_picas(self,pref_type="",add_keys={}):
        LRT.submit_to_picas(self,token_type="pref"+pref_type,keys=add_keys,attfile=self.parsetfile)

    def start_jdl(self):
        LRT.start_jdl(self)
