#!/bin/bash

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
STARTSB=${1}
NUMSB=${2}
PARSET=${3}
LOFAR_PATH=${4}


if [ -d /cvmfs/softdrive.nl ]
  then
    echo "Softdrive directory found"
 else
	echo "softdrive not found"
	exit 10 #exit 10=>softdrive not mounted
fi


echo "INITIALIZE LOFAR FROM SOFTDRIVE, in "$LOFAR_PATH

function log(){
if [ -z "$2" ]
  then
    echo "                     |"${1}
  else
     printf "%20s %s" ${1}
     printf "|"${2}
     printf "\n"
fi 
}
######while read -r line; do log  "$line"; done <<<"$output"
#### use above code to print out command result 
function setup_env(){
 if [ -z "$1" ]
  then
    echo "Initializing default environment"
    . /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/init_env_release.sh
    export PYTHONPATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
  LOFAR_PATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/
  else
    if [ -e "$1/init_env_release.sh" ]; then
      echo "Initializing environment from ${1}"
      . ${1}/init_env_release.sh
      export PYTHONPATH=${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
      export LOFARDATAROOT=/cvmfs/softdrive.nl/wjvriend/data
    else
	echo "The environment script doesn't exist. check the path $1 again"
	exit 11 #exit 11=> no init_env script
    fi
  fi  
}

setup_env $LOFAR_PATH

# NEW NB we can't assume the home dir is shared across all Grid nodes.
log  "var LOFARDATAROOT: " ${LOFARDATAROOT}
log  "setup" "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"
ln -s ${LOFARDATAROOT} .
ln -s ${LOFARDATAROOT} ~/

log "setup" "generic pipeline is at $( which genericpipeline.py )"
#set -x
#Detect segmentation violation and exit
trap '{ echo "Trap detected segmentation fault... status=$?"; exit 2; }' SIGSEGV #exit 2=> SIGSEGV caught

log  ""
log  "-----------------------------------------------------------------------"
log  "Obtain information for the Worker Node and set the LOFAR environment"
log  "----------------------------------------------------------------------"

log "-"
log "worker info" `date`
log "worker info"  $HOSTNAME
log "worker info" $HOME

log "worker info" "-"
log "worker info" "Job directory is:"
log "worker info" $PWD
ls -l $PWD

log "-"
log "worker info" "WN Architecture is:"
cat /proc/meminfo | grep "MemTotal"
cat /proc/cpuinfo | grep "model name"


# initialize job arguments
# - note, obsid is only used to store the data

log "++++++++++++++++++++++++++++++"
log "++++++++++++++++++++++++++++++"

log "job info" "INITIALIZATION OF JOB ARGUMENTS"
log "job info" ${JOBDIR}
log "job info" ${STARTSB}
log "job info" ${NUMSB}
log "job info" ${PARSET}
log 


# create a temporary working directory
RUNDIR=`mktemp -d -p $TMPDIR`
cp $PWD/prefactor.tar $RUNDIR
cp -r $PWD/openTSDB_tcollector $RUNDIR
mkdir $RUNDIR/piechart
cp -r $PWD/piechart/* $RUNDIR/piechart 
cp pipeline.cfg $RUNDIR
cd ${RUNDIR}
echo "untarring Prefactor" 
tar -xf prefactor.tar
cp prefactor/srm.txt $RUNDIR

sed -i "s?LOFAR_ROOT?${LOFAR_PATH}?g" pipeline.cfg
echo "replaced LOFAR_PATH in pipeline.cfg"
pwd
touch activejobs
echo ""
echo "---------------------------------------------------------------------------"
echo "START PROCESSING" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"

#CHECKING FREE DISKSPACE AND FREE MEMORY AT CURRENT TIME
echo ""
echo "current data and time"
date
echo "free disk space"
df -h .
echo "free memory"
free 
freespace=`stat --format "%a*%s/1024^3" -f $TMPDIR|bc`
echo "Free scratch space "$freespace"GB"


#STEP2 
####
# Download the data on the node 10 subbands at a time while ignoring subbands that 
# cannot be downloaded (so that the job doesn't hang)
####
echo ""
echo "---------------------------"
echo "Starting Data Retrieval"
echo "---------------------------"
echo "Get subbands "


sleep 6


sed -n -e '/SB'$STARTSB'/,$p' srm.txt > srm-stripped.txt
OBSID=$(echo $(head -1 srm-stripped.txt) |grep -Po "L[0-9]*" | head -1 )
head -n $NUMSB srm-stripped.txt |grep $OBSID > srm-final.txt
echo "processing parset " $PARSET

if [ ! -z $( echo $PARSET | grep Initial-Subtract ) ] #parset must have Initial-Subtract*.parset
 then
  echo ""
  echo "processing INITIAL-SUBTRACT Parset ${PARSET}"
  echo ""
  echo "Setting download of subbands in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/ |grep $OBSID |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  rm -rf srm*txt
  grep $STARTSB gsiftps_init.txt > srm-final.txt
fi

echo "Final srms tp download"
cat srm-final.txt


NUMLINES=$(( $(wc -l srm-final.txt |awk '{print $1}' ) )) #WHAT USE IS THIS?
echo "Downloading files"
python ./prefactor/bin/download_srms.py srm-final.txt &

wait

##TODO:Wait for all tarfiles!
# - step2 finished check contents
echo "step2 finished, list contents"
ls -l $PWD
du -hs $PWD
du -hs $PWD/*

# SETTINGS FOR PYTHON PROCESSING
dirc=${RUNDIR}
name=${new_name}
path=${dirc}/${name}

parset=${PARSET}
sbn=${SUBBAND_NUM}


echo "Replacing "$PWD" in the prefactor parset"

sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" $parset
sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" pipeline.cfg
echo "Concatinating only "${NUMLINES}" Subbands"
sed -i "s?num_SBs_per_group.*?num_SBs_per_group    = ${NUMLINES}?g" $parset

#Check if any files match the target, if so, download the calibration tables matching the calibrator OBSID. If no tables are downloaded, xit with an error message.
if [[ ! -z $( grep " target_input_pattern =" prefactor/Pre-Facet-Cal.parset | awk '{print $NF}' | xargs find . -name )  ]]
then
 CAL_OBSID=$( grep "cal_input_pattern " prefactor/Pre-Facet-Cal.parset | grep -v "}" | awk '{print $NF}' | awk -F "*" '{print $1}' )
 echo "Getting solutions from obsid "$CAL_OBSID
 globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/numpy_$CAL_OBSID.tar file:`pwd`/numpys.tar
 if [[ -e numpys.tar ]]
  then
    tar -xvf numpys.tar
 else
    exit 1
 fi
fi

if [[ ! -z ${CAL_OBSID} ]]
then
pipelinetype="pref.targ"
elif [[ ! -z $( echo $PARSET | grep Initial-Subtract ) ]]
then
pipelinetype="pref.insub"
else
pipelinetype="pref.cal"
fi

echo "Pipeline type is "$pipelinetype
echo "Adding $OBSID and $pipelinetype into the tcollector tags"
sed -i "s?\[\]?\[\ \"obsid=${OBSID}\",\ \"pipeline=${pipelinetype}\"\]?g" openTSDB_tcollector/collectors/etc/config.py

echo "start tCollector in dryrun mode"
cd openTSDB_tcollector/
mkdir logs
./tcollector.py -d > tcollector.out &
TCOLL_PID=$!
cd ..

echo ""
echo "execute generic pipeline"
genericpipeline.py $parset -d -c pipeline.cfg > output

echo "killing tcollector"
kill $TCOLL_PID

xmlfile=$( find . -name "*statistics.xml" 2>/dev/null)
./piechart/make_a_pie.py ${xmlfile} PIE_${xmlfile}.png

find . -name "*png"|xargs tar -zcf pngs.tar.gz
find . -name "*npy"|xargs tar -cf numpys.tar
tar --append --file=numpys.tar pngs.tar.gz
find . -name "*tcollector.out" | xargs tar -cf profile.tar
find . -iname "*statistics.xml" -exec tar -rvf profile.tar {} \;
find . -name "*png" -exec tar -rvf profile.tar {} \;
tar --append --file=profile.tar output
tar -zcvf profile.tar.gz profile.tar
find . -iname "*h5" -exec tar -rvf numpys.tar {} \;


cp pngs.tar.gz ${JOBDIR}
echo "Numpy files found:"
find . -name "*npy"
#
# - step3 finished check contents
more output
OBSID=$( echo $(head -1 srm.txt) |grep -Po "L[0-9]*" | head -1 )
echo "Saving profiling data to profile_"$OBSID_$( date  +%s )".tar.gz"
globus-url-copy file:`pwd`/profile.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/profiling/profile_${OBSID}_$( date  +%s ).tar.gz
if [[ $( grep "finished unsuccesfully" output) > "" ]]
then
     echo "Pipeline did not finish, tarring work and run directories for re-run"
     RERUN_FILE=$OBSID"_"$STARTSB"prefactor_error.tar"
     echo "Will be  at gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/error_states"$RERUN_FILE
     tar -cf $RERUN_FILE prefactor/
     globus-url-copy file:`pwd`/$RERUN_FILE gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/error_states/$RERUN_FILE
   if [[ $(hostname -s) != 'loui' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR}
   fi
   if [[ $( grep "bad_alloc" output) > "" ]]
   then
	echo "Prefactor crashed because of bad_alloc. Not enough memory"
	exit 16
   fi
   exit 1
fi 

echo "step3 finished, list contents"

#python log contents

# read -p "Press [Enter] key to continue..."



# STORE PROCESSING RESULTS AND CLEAN UP
echo ""
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

echo "JOBDIR, RUNDIR, PWD: ", ${JOBDIR}, ${RUNDIR}, ${PWD}
#ls -l ${JOBDIR}
#ls -l ${RUNDIR}
#ls -l ${PWD}
#du -hs $PWD
#du -hs $PWD/*

echo "Copy output to the Grid SE"





# copy the output tarball to the Grid storage
OBSID=$( echo $(head -1 srm.txt) |grep -Po "L[0-9]*" | head -1 )

echo "copying the Results"
#globus-url-copy file:`pwd`/instruments.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/instr_$OBSID.tar

if [ ! -z $( echo $PARSET | grep Initial-Subtract ) ]
   then
   OBSID="Init_"${OBSID}
   CAL_OBSID="2" #do this nicer
fi

if [[ ! -z $CAL_OBSID ]]
then
	tar -zcvf results.tar.gz prefactor/results/*
	globus-url-copy file:`pwd`/results.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/results_${OBSID}_SB${STARTSB}_.tar.gz
else
	 globus-url-copy file:`pwd`/numpys.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/numpy_$OBSID.tar
fi

# Exit loop on non-zero exit status:
if [[ "$?" != "0" ]]; then
   echo "Problem copying final files to the Grid. Clean up and Exit now..."
   cp log_$name logtar_$name.fa ${JOBDIR}
   cd ${JOBDIR}

   if [[ $(hostname -s) != 'loui' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR} 
   fi
   exit 1
fi

echo ""
echo "List the files copied to the SE lofar/user/disk:"
#srmls srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
#uberftp -ls gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
#
echo ""

echo ""
echo "copy logs to the Job home directory and clean temp files in scratch"
cp out* ${JOBDIR}
cd ${JOBDIR}
cp pngs.tar.gz ${JOBDIR}

if [[ $(hostname -s) != 'loui' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR} 
fi
ls -l ${RUNDIR}
echo ""
echo "listing final files in Job directory"
ls -allh $PWD
echo ""
du -hs $PWD


echo ""
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"

