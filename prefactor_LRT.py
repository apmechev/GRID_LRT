#!/bin/env python
##########################
#Python script to check SURLS, stage files, create and run tokens
#
#Usage python fad.py srm_L229587.txt master_setup.cfg
# fad_v7- 	Add Y/N
#		Added check for proper input and srm filename
#		Added check for staging and if staging succeeded
#version 1.1-   17-Mar-2016
#version 1.2 -  3-Apr-2016
#		Now accepts a default parset with no master_setup
#		7-Apr-2016
#		Now accepts user defined parset in FAD_v#/parsets in custom_setup
#		Can Invoke scripts to modify parset on the node
#		--resubmit errors only implemented 
#TODO: Check if skymodel exists before running?
#TODO: annotate srms with target/calibrator to help user for many many OBSIDs in one file
##########################

if __name__ == "__main__":
        import sys
        sys.path.append('./LRT/classes')
        from class_prefactor_LRT import pref_LRT
        
        pf=pref_LRT()
        pf.parse_arguments(sys.argv) 
	pf.splitsrms()               
	pf.setup_dirs()              

#        pf.prepare_sandbox()

        pf.check_state_and_stage()
	
	####################
	##Wait for keystroke
	###################

	yes = set(['yes','y', 'ye','yea','yesh','Y','oui', ''])
	no = set(['no','n','N'])
	print ""
        print "Do you want to continue? Y/N (Enter continues)"

	from termios import tcflush, TCIOFLUSH
	tcflush(sys.stdin, TCIOFLUSH) #Flush input buffer to stop enter-spammers
	choice = raw_input().lower()

	if choice in yes:
	   pass
	elif choice in no:
	   sys.exit()
	else:
	   sys.exit()

	pf.submit_to_picas()
	pf.start_jdl()
	sys.exit()


