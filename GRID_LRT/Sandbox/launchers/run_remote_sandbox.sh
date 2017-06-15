# ============================================================================================  #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara	                        #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara	                        #
#                                                     		                                #
# usage: ./run_remote_sandbox.sh [picas_db_name] [picas_username] [picas_pwd] [token_type] 	#
# description: Get grid tools from github, and launch getOBSID which takes a token of the type  #
#	       specified, downloads the appropriate sandbox and executes it                     #
#                                                                                               #
#          apmechev: Modified and frozen to standardize job launching                           #
#          - Sept 2016                                                                          #
#                                                                                               #
# ============================================================================================  #

set -x

#Clones the picas tools repository which interfaces with the token pool
#uses wget if no git

if type git &> /dev/null
then
 git clone https://github.com/apmechev/GRID_picastools.git p_tools_git
else
 wget https://github.com/apmechev/GRID_picastools/archive/master.zip
 unzip master.zip -d p_tools_git/ 
fi

mv p_tools_git/* . 
rm -rf p_tools_git/

echo "Pulling down the sandbox for OBSID "$OBSID" from /pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox/sandbox_$2_$OBSID.tar with token type $4"

###Traps
trap '{ echo "Trap detected segmentation fault... status=$?"; $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} "segfault"; sleep 5; rm -rf ${RUNDIR}/*;  exit 2; }' SIGSEGV #exit 2=> SIGSEGV caught
trap '{ echo "Trap detected interrupt ..."; $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} "interrupted"; sleep 2;  exit 3; }' SIGHUP SIGINT SIGTERM  #exit 3=> Interrupted by signal

#launches script designed to lock token, download sandbox with 
#token's OBSID and execute the master.sh in the sandbox
/usr/bin/python getSBX.py $1 $2 $3 $4 &
wait

ls -l
cat log*
