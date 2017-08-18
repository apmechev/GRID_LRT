#!/bin/bash
touch log
echo "" > log
# ===================================================================== #
# authors: Alexandar Mechev <apmechev@strw.leidenuniv.nl> --Leiden	#
#	   Natalie Danezi <anatoli.danezi@surfsara.nl>  --  SURFsara    #
#          J.B.R. Oonk <oonk@strw.leidenuniv.nl>    -- Leiden/ASTRON    #
#                                                                       #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: ./prefactor.sh [OBSID] [SURL_SUBBAND] 	                        #
#        [AVG_FREQ_STEP] [AVG_TIME_STEP] [DO_DEMIX] [DEMIX_FREQ_STEP]	#
#	 [DEMIX_TIME_STEP] [DEMIX_SOURCES] [SELECT_NL]                  #
#                                                                       #
#  note: demixer.freqstep = [AVG_FREQ_STEP] 'averages data in freq'     #
#        demixer.timestep = [AVG_TIME_STEP] 'averages data in time'     #
#        demixer.demixfreqstep = [DEMIX_FREQ_STEP] 'demix done on time' #
#        demixer.demixtimestep = [DEMIX_TIME_STEP] 'demix done on time' #
#                                                                       #
#        SELECT_NL (bool): True = keep only NL , False=keep all         #
#        DO_DEMIX  (bool): True or False                                #
#        DEMIX_SOURCES (string): user defined ( ex. [Cas,CygA] )        #
#                                                                       #
#  note: add 'Ateam_LBA.sky.tar' to sandbox and untar in avg_dmx.py     #
#                                                                       #
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

########################
### Importing functions
########################

for i in `ls bin/*sh`; do source $i; done

echo "INITIALIZE LOFAR FROM SOFTDRIVE, in "$LOFAR_PATH

setup_LOFAR_env $LOFAR_PATH      ##Imported from setup_LOFAR_env.sh
setup_DDF_env $DDF_PATH

${OLD_PYTHON} set_token_field.py sksp_dev  $TOKEN status starting

# NEW NB we can't assume the home dir is shared across all Grid nodes.
trap '{ echo "Trap detected segmentation fault... status=$?"; exit 2; }' SIGSEGV #exit 2=> SIGSEGV caught

# create a temporary working directory #This depends on host!
setup_run_dir   #imported from setup_run_dir.sh
print_info

sed -i "s?LOFAR_ROOT?${LOFAR_PATH}?g" parset.cfg
echo  "replaced LOFAR_PATH in parset/cfg"
pwd

echo ""
echo "---------------------------------------------------------------------------"
echo "START PROCESSING" $OBSID "SUBBAND:" $STARTSB
echo "---------------------------------------------------------------------------"
#STEP2 

echo ""
echo "---------------------------"
echo "Starting Data Retrieval"
echo "---------------------------"
echo "Get subbands "

sleep 6

setup_downloads $PIPELINE

echo "Downloading $NUMSB files"

ls >> log

download_files srm.txt $PIPELINE

du -hs */ 
# - step2 finished check contents
echo "step2 finished, list contents"
ls -l $PWD
du -hs $PWD
du -hs $PWD/*

# SETTINGS FOR PYTHON PROCESSING

echo "Replacing "$PWD" in the prefactor parset"

#Check if any files match the target, if so, download the calibration tables matching the calibrator OBSID. If no tables are downloaded, xit with an error message.

pipelinetype=$PIPELINE

echo "Pipeline type is "$pipelinetype
echo "Adding $OBSID and $pipelinetype into the tcollector tags"
sed -i "s?\[\]?\[\ \"obsid=${OBSID}\",\ \"pipeline=${pipelinetype}\"\]?g" openTSDB_tcollector/collectors/etc/config.py

echo ""
echo "execute ddf-pipeline"

ln -s ${LOFARDATAROOT} .
ln -s ${LOFARDATAROOT} ~/

CleanSHM.py
#export PATH=$PWD/ddf-pipeline:$PATH
#export PYTHONPATH=$PWD/ddf-pipeline:$PYTHONPATH

setup_ddf-pipeline

run_pipeline

rm -rf *.tar.gz

rm -rf ddf-pipeline/

upload_results

#cleanup
# STORE PROCESSING RESULTS AND CLEAN UP
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"

