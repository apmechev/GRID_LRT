#!/bin/env python
##########################
#Python script to check to create tokens fro LGPPP
#
#Usage python fad.py srm_L229587.txt master_setup.cfg
# fad_v7- 	Add Y/N
#		Added check for proper input and srm filename
#		Added check for staging and if staging succeeded
#version 1.1-   17-Mar-2016
#version 1.2-   3-Apr-2016
#		Now accepts a default parset with no master_setup
#		7-Apr-2016
#		Now accepts user defined parset in FAD_v#/parsets in custom_setup
#		Can Invoke scripts to modify parset on the node
#		--resubmit errors only implemented
#
# Branch-off for LGPPP
#  version 0.1-  20-09-2016 JBR OONK (Leiden/ASTRON)
#
#                 replace_in_file(..)     -> user side
#                 parse_arguments(..)     -> user side
#                 setup_dirs()            -> user side
#
#                 check_state_and_stage() -> grid side (*)               
#                 prepare_sandbox()       -> grid side (*)  
#                 start_jdl()             -> grid side (*)  
#
#                To run first set below environment variables (e.g. ~/.bashrc)
#
#                 export PICAS_USR=xxxxxx
#                 export PICAS_USR_PWD=xxxxxx
#                 export PICAS_DB=xxxxxx
#
# to run on the grid (prod): /home/oonk/LGPPP_GRD/GRID_LRT
# $ ./LGPPP_GRD.py srm_dummy.txt default_parset.cfg
#
# to run on loui (test): /home/oonk/LGPPP_GRD/GRID_LRT/LRT/Application
# $ . startpilot.sh $PICAS_DB $PICAS_USR $PICAS_USR_PWD
#
# note1: I had to manually tar the scripts directory first (bug?)
#
# note2: I moved 'std' sandbox to old_sandbox
# Error - 
# InputSandbox: Specified path 'sandbox/run_remote_sandbox.sh' is missing
#
# Traceback (most recent call last):
#  File "./LGPPP_GRD.py", line 80, in <module>
#    f.start_jdl()
#  File "./LRT/classes/class_FAD_LRT.py", line 59, in start_jdl
#  File "./LRT/classes/class_default_LRT.py", line 304, in start_jdl
# IOError: [Errno 2] No such file or directory: 'jobIDs'
#
# => I fixed this by manually copying the lgppp_sandbox to sandbox and rerunning!
#
##########################

import os, sys

if __name__ == "__main__":

        print "starting LGPPP_GRD"
        import sys
        sys.path.append('./LRT/classes')
        from class_FAD_LRT import FAD_LRT
        
        f=FAD_LRT()

        f.parse_arguments(sys.argv) 
        # QUERY 'todo' TOKENS to generate an srmlist (could many obsid's and users)    
	sys.path.append('./LRT/Tokens')

	import Token
	th=Token.Token_Handler(uname=os.environ["PICAS_USR"],pwd=os.environ["PICAS_USR_PWD"],dbn=os.environ["PICAS_DB"],t_type="token")
	th.add_view("todo",'doc.lock == 0 && doc.done == 0')
	token_srms=[]	
	v = th.db.view(th.t_type+"/todo")
	for x in v:
		document = th.db[x['key']]
		token_srms.append(document['SURL_SUBBAND'])
	print token_srms

	with open("srm.txt",'w') as surlfile:
		for s in token_srms:
			surlfile.write(s)

	f.srmfile=os.path.abspath("srm.txt")

	f.setup_dirs()
        f.prepare_sandbox('/home/oonk/LGPPP_GRD/GRID_LRT/LRT/Application/lgppp-sandbox')
        f.check_state_and_stage()
        print "the f class has so this percent unstaged "+str(f.unstaged)	

        f.start_jdl()


