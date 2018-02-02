#!/bin/bash

# ===================================================================== #
# authors: Alexandar Mechev <apmechev@strw.leidenuniv.nl> --Leiden	#
#	   Natalie Danezi <anatoli.danezi@surfsara.nl>  --  SURFsara    #
#          J.B.R. Oonk <oonk@strw.leidenuniv.nl>    -- Leiden/ASTRON    #
#                                                                       #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: ./master.sh [OPTIONS]                                          #
#                                                                       #
# description:                                                          #
#       Set Lofar environment, fetch input from Grid Storage,           #
#       do averaging or demixing, then flag output with std. strategy,  #
#       finally copy the output to a (temporary) Grid Storage           #
# ===================================================================== #

#--- NEW SD ---
JOBDIR=${PWD}
OLD_PYTHON=$( which python)
echo $OLD_PYTHON

if [ -z "$TOKEN" ] || [  -z "$PICAS_USR" ] || [  -z "$PICAS_USR_PWD" ] || [  -z "$PICAS_DB" ]
 then
  echo "One of Token=${TOKEN}, Picas_usr=${PICAS_USR}, Picas_db=${PICAS_DB} not set"; exit 1 
fi


########################
### Importing functions
########################

for setupfile in `ls bin/* `; do source ${setupfile} ; done


############################
#Initialize the environment
############################

setup_LOFAR_env $LOFAR_PATH      ##Imported from setup_LOFAR_env.sh

#trap cleanup EXIT #This ensures the script cleans_up regardless of how and where it exits

print_worker_info                      ##Imported from bin/print_worker_info

if [[ -z "$PARSET" ]]; then
    ls "$PARSET"
    echo "not found"
    exit 3  #exit 3=> Parset doesn't exist
fi

setup_run_dir                     #imported from bin/setup_run_dir.sh

print_job_info                  #imported from bin/print_job_info.sh

echo ""
echo "---------------------------------------------------------------------------"
echo "START PROCESSING" $OBSID "SUBBAND:" $STARTSB
echo "---------------------------------------------------------------------------"
echo ""
echo "---------------------------"
echo "Starting Data Retrieval"
echo "---------------------------"

setup_downloads $PIPELINE

download_files srm.txt $PIPELINE

echo "Download finished, list contents"
ls -l $PWD
du -hs $PWD

replace_dirs            #imported from bin/modify_files.sh

if [[ ! -z ${CAL_OBSID}  ]]
then
 download_cals $CAL_OBSID
fi

if [[ ! -z $( echo $PIPELINE |grep targ1 ) ]]
  then
    runtaql 
fi


#########
#Starting processing
#########

start_profile

run_pipeline

stop_profile

process_output output


#####################
# Make plots
#
######################

make_plots
make_pie
# - step3 finished check contents

upload_results

cleanup 

echo ""
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED PROCESSING TOKEN " ${TOKEN}
echo "---------------------------------------------------------------------------"
