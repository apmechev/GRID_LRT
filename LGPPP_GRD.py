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
##########################


# QUERY 'todo' TOKENS to generate an srmlist (could many obsid's and users)

