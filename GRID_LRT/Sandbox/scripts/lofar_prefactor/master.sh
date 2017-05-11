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

#source bin/setup_lofar_env.sh
#source bin/print_worker_info.sh
#source bin/setup_downloads.sh 
#source bin/setup_run_dir.sh
#source bin/print_job_info.sh
#source bin/download.sh
#source bin/download_cal_sols.sh
#source bin/targ2_process.sh
#source bin/profile.sh
#source bin/process.sh
#source bin/process_prefactor_output.sh
#source bin/plot.sh
#source bin/save_logs.sh
#source bin/upload_results.sh
#source bin/cleanup.sh
#source bin/modify_files.sh


#TEMP=`getopt -o oclspTtduw: --long obsid:,calobsid:,lofdir:,startsb:,parset:,pipetype:,token:,picasdb:,picasuname:,picaspwd: -- "$@"`
#if [ $? != 0 ] ; then echo "Terminating..." >&2 ; exit 9 ; fi #exit 9=> master.sh got bad argument
#
#PARSET="Pre-Facet-Target.parset"
#eval set -- "$TEMP"
#echo $TEMP
#while [ true ]
#do
#    case $1 in
#    -o | --obsid ) OBSID="$2" ; shift  ;;
#    -c | --calobsid ) CAL_OBSID="$2"; shift  ;;
#    -l | --lofdir ) LOFAR_PATH="$2";shift ;;
#    -s | --startsb) STARTSB="$2";shift ;;
#    -p | --parset ) PARSET="$2"; shift  ;;
#    -T | --pipetype ) PIPELINE="$2"; shift ;;
#    -t | --token ) TOKEN="$2"; shift  ;;         #Put these in the env before so scripts aren't responsible for it, but the framework is???
#    -d | --picasdb ) PICAS_DB="$2"; shift ;;     #..??????
#    -u | --picasuname ) PICAS_USR="$2"; shift ;; #..??????
#    -w | --picaspwd ) PICAS_USR_PWD="$2" ; shift ;;
#    -- ) shift; break;;
#    -*) echo "$0: error - unrecognized option $1" 1>&2; exit 8;; #exit 8=> Unknown argument
#    * ) break;;
#    esac
#    shift
#done


############################
#Initialize the environment
############################

setup_LOFAR_env $LOFAR_PATH      ##Imported from setup_LOFAR_env.sh

#trap cleanup EXIT #This ensures the script cleans_up regardless of how and where it exits

print_info                      ##Imported from bin/print_worker_info

if [[ -z "$PARSET" ]]; then
    ls "$PARSET"
    echo "not found"
    exit 30  #exit 30=> Parset doesn't exist
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

#start_profile

run_pipeline

#stop_profile

process_output output


#####################
# Make plots
#
######################

make_plots

tarlogs 

# - step3 finished check contents

#more openTSDB_tcollector/logs/*
#OBSID=$( echo $(head -1 srm.txt) |grep -Po "L[0-9]*" | head -1 )
#echo "Saving profiling data to profile_"$OBSID_$( date  +%s )".tar.gz"
#globus-url-copy file:`pwd`/profile.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/profiling/profile_${OBSID}_$( date  +%s ).tar.gz &
#wait

upload_results

cleanup 

echo ""
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED PROCESSING TOKEN " ${TOKEN}
echo "---------------------------------------------------------------------------"
