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


function clean_dl_pids() {

 for line in `seq 1 $(wc -l activejobs|awk '{print $1}')`
  do
   dlprocess=$(cat activejobs|head -$line |tail -1 |awk '{print $1}')
   dlSB=$(cat activejobs|head -$line |tail -1 |awk '{print $2}')
   if [[ ! -f /proc/$dlprocess/net/dev ]]; then
       if [[ $(du -s $dlSB 2>/dev/null |awk '{print $1}') != '000000' ]]; then
         sed -i $line's/.*/done '$dlSB'/' activejobs
         continue
       fi
   fi  ##use du hs on the directory for download or find pid of globus
   download=$(du -s $dlSB 2>/dev/null |awk '{print $1}') 
   if [[ $download == "" ]]; then
       download=000000
   fi 
   sed -i $line's/.*/'$dlprocess' '$dlSB' '$download'/' activejobs
      echo "Process "$dlprocess" has untarred "$download"b in "$dlSB
done

}


#--- NEW SD ---

echo "START LOFAR FROM SOFTDRIVE"
echo "Setting up the LOFAR environment; setting release"

#LOFAR SOFTWARE SOFTDRIVE VERSION
# 2.16
#
USR_LOFAR_VERSION=2.16
echo "USR_LOFAR_VERSION", ${USR_LOFAR_VERSION}

# TEST
VO_LOFAR_SW_DIR=/cvmfs/softdrive.nl/wjvriend/lofar_stack/

LOFARROOT=${VO_LOFAR_SW_DIR}/${USR_LOFAR_VERSION}/lofar/release
echo "LOFARROOT: ", ${LOFARROOT}
export LOFARROOT

# NEW INIT VIA init_env_release.sh
#echo "source init_env_release.sh" || exit 1
. /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/init_env_release.sh 

# NEW NB we can't assume the home dir is shared across all Grid nodes.
echo "LOFARDATAROOT: ", ${LOFARDATAROOT}
echo "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"
ln -s ${LOFARDATAROOT} ~/

#losoto path
echo "Exporting LoSoTo path"
export PYTHONPATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH


##set -x
#Detect segmentation violation and exit
trap '{ echo "Trap detected segmentation fault... status=$?"; exit 1; }' SIGSEGV

echo ""
echo "----------------------------------------------------------------------"
echo "Obtain information for the Worker Node and set the LOFAR environment"
echo "----------------------------------------------------------------------"

echo ""
echo `date`
echo $HOSTNAME
echo $HOME
echo $VO_LOFAR_SW_DIR
ls -l $VO_LOFAR_SW_DIR

echo ""
echo "Job directory is:"
echo $PWD
ls -l $PWD

echo ""
echo "WN Architecture is:"
cat /proc/meminfo | grep "MemTotal"
cat /proc/cpuinfo | grep "model name"


# initialize job arguments
# - note, obsid is only used to store the data
JOBDIR=${PWD}
STARTSB=${1}
ENDSB=${2}
SRMFILE=${3}

echo "++++++++++++++++++++++++++++++"
echo "++++++++++++++++++++++++++++++"

echo "INITIALIZATION OF JOB ARGUMENTS"
echo ${JOBDIR}
echo ${STARTSB}
echo ${ENDSB}
echo ${SRMFILE}
echo ""


# create a temporary working directory
RUNDIR=`mktemp -d -p $TMPDIR`
cp $PWD/prefactor.tar $RUNDIR
cd ${RUNDIR}
echo "untarring Prefactor" 
tar -xf prefactor.tar
cp prefactor/srm.txt $RUNDIR

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

for block in `seq 1 5`; do 
 let init=" ($block - 1) * 10 + 1"
 let fin=" $block * 10"
 ./prefactor/bin/download_num_files.sh $init $fin srm.txt  &

 #DL_PID=$!
 #cat /proc/$DL_PID/net/dev

sleep 10
 
 STALLED=0
 NUMJOBS=244
set +x
 while [ $NUMJOBS -ge 2 ]
  do
     echo $NUMJOBS
     clean_dl_pids 

     LENJOBS=$(wc -l activejobs | awk '{print $1}')
     NUMDONE=$(grep 'done' activejobs |wc -l |awk '{print $1}' )
     STALLED=$(grep '000000' activejobs |wc -l|awk '{print $1}')
      if [[ $NUMDONE == "" ]]; then 
        NUMDONE=0
      fi
      if [[ $STALLED == "" ]]; then 
        STALLED=0
      fi
     NUMJOBS=$(( $LENJOBS - $NUMDONE ))
     echo $NUMJOBS" Subbands remaining "$STALLED" have stalled"
     sleep 60
     if [[ $(( $NUMDONE + $STALLED )) -eq $LENJOBS ]]; then
       break
     fi
  done
set -x
 echo "Done downloading, killing stalled jobs"
 sleep 15
  
 for line in `seq 1 $(wc -l activejobs|awk '{print $1}')`
  do
    killPID=$(cat activejobs |head -$line |tail -1 |awk '{print $1}')
    if [[ ! $killPID == "-" ]]; then
    kill $killPID
    echo "Killed stalled download process "$killPID
      fi
  done
  echo "" > activejobs
done


#while [[ $(ps -aux |grep tar| wc -l |awk '{print $1}') > 1 ]]
#do
#sleep 120
#done


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
avg_freq_step=${AVG_FREQ_STEP}
avg_time_step=${AVG_TIME_STEP}
do_demix=${DO_DEMIX}
demix_freq_step=${DEMIX_FREQ_STEP}
demix_time_step=${DEMIX_TIME_STEP}
demix_sources=${DEMIX_SOURCES}
select_nl=${SELECT_NL}

parset=${PARSET}
sbn=${SUBBAND_NUM}


echo "Replacing "$PWD" in the prefactor parset"

sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" prefactor/Pre-Facet-Cal.parset 
sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" prefactor/pipeline.cfg

echo ""
echo "execute generic pipeline"
genericpipeline.py ./prefactor/Pre-Facet-Cal.parset -d -c prefactor/pipeline.cfg > out-test-1

#
# - step3 finished check contents
echo "step3 finished, list contents"

#python log contents

# read -p "Press [Enter] key to continue..."



# STORE PROCESSING RESULTS AND CLEAN UP
echo ""
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

echo "JOBDIR, RUNDIR, PWD: ", ${JOBDIR}, ${RUNDIR}, ${PWD}
ls -l ${JOBDIR}
ls -l ${RUNDIR}
ls -l ${PWD}
du -hs $PWD
du -hs $PWD/*




echo "Tarring instrument tables (TODO):"
find . -name "instrument" | xargs tar -cvf instruments.tar
echo "Copy output to the Grid SE"
du -hs instruments.tar
more out-test-1

# remove any old existing directory from the Grid storage
uberftp -rm -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
# create the output directory on the Grid storage
uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/
# copy the output tarball to the Grid storage
OBSID=$(echo $(head -1 srm.txt) |grep -Po "L[0-9]*" | head -1 )
echo "copying the instrument tables into <storage>/spectroscopy/prefactor/instr_"$OBSID.tar
globus-url-copy file:`pwd`/instruments.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/instr_$OBSID.tar
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
uberftp -ls gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
#
echo ""

echo ""
echo "copy logs to the Job home directory and clean temp files in scratch"
cp out* ${JOBDIR}
cd ${JOBDIR}

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
du -hs $PWD/*

echo ""
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"