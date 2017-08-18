#!/bin/env python 


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

    def prepare_srms(self):
        '''This now exists for legacy support, it's all done in 
            check_state_and_stage()
        '''
        print ""
        print "You're running \033[33m SARA LRT1.5\033[0m, default"
        print ""
        from GRID_LRT.Staging import srmlist
        self.Srm_obj=class_srmlist.Srm_manager(OBSID=self.OBSID,stride=self.numpernode)
        self.Srm_obj.file_load(self.srmfile)
        self.srms=self.Srm_obj.srms

    def prepare_sandbox(self):
        import class_sandbox
