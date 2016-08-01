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


if [ -d /cvmfs/softdrive.nl ]
  then
    echo "Softdrive directory found"
 else
	echo "softdrive not found"
	exit 1
fi


echo "START LOFAR FROM SOFTDRIVE"
echo "Setting up the LOFAR environment; setting release"

#LOFAR SOFTWARE SOFTDRIVE VERSION
# current
#
#USR_LOFAR_VERSION=current
#echo "USR_LOFAR_VERSION", ${USR_LOFAR_VERSION}

# TEST
#VO_LOFAR_SW_DIR=$VO_LOFAR_SW_DIR/

#LOFARROOT=${VO_LOFAR_SW_DIR}/${USR_LOFAR_VERSION}/lofar/release
#echo "LOFARROOT: ", ${LOFARROOT}
#export LOFARROOT

# NEW INIT VIA init_env_release.sh
#echo "source init_env_release.sh" || exit 1
. /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/init_env_release.sh 
export PYTHONPATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH

# NEW NB we can't assume the home dir is shared across all Grid nodes.
echo "LOFARDATAROOT: ", ${LOFARDATAROOT}
echo "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"
ln -s ${LOFARDATAROOT} .
ln -s ${LOFARDATAROOT} ~/

which genericpipeline.py
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
NUMSB=${2}
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
cp -r $PWD/openTSDB_tcollector $RUNDIR
mkdir $RUNDIR/piechart
cp -r $PWD/piechart/* $RUNDIR/piechart 
cp pipeline.cfg $RUNDIR
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
echo "Final srm"
cat srm-final.txt

NUMLINES=$(( $(wc -l srm-final.txt |awk '{print $1}' )/10 + 1 )) #WHAT USE IS THIS?

for block in `seq 1 $(( NUMSB / 10 ))`; do
 let init=" ($block - 1) * 10 + 1"
 let fin=" $block * 10"
 ./prefactor/bin/download_num_files.sh $init $fin srm-final.txt  &


sleep 10
 
 STALLED=0
 NUMJOBS=244
set +x
 while [ $NUMJOBS  -ge 1  ]
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
     sleep 30
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

parset=${PARSET}
sbn=${SUBBAND_NUM}


echo "Replacing "$PWD" in the prefactor parset"

sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" prefactor/Pre-Facet-Cal.parset 
sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" pipeline.cfg
echo "Concatinating only "${NUMLINES}" Subbands"
sed -i "s?num_SBs_per_group.*?num_SBs_per_group    = ${NUMLINES}?g" prefactor/Pre-Facet-Cal.parset

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


echo "start tCollector in dryrun mode"
cd openTSDB_tcollector/
mkdir logs
./tcollector.py -d > tcollector.out &
TCOLL_PID=$!
cd ..

echo ""
echo "execute generic pipeline"
genericpipeline.py ./prefactor/Pre-Facet-Cal.parset -d -c pipeline.cfg > output

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

echo "copying the instrument tables into <storage>/spectroscopy/prefactor/instr_"$OBSID.tar
#globus-url-copy file:`pwd`/instruments.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/instr_$OBSID.tar
if [[ ! -z $CAL_OBSID ]]
then
	tar -zcvf results.tar.gz prefactor/results/*
	globus-url-copy file:`pwd`/results.tar.gz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/prefactor/results_${OBSID}_${STARTSB}.tar.gz
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
du -hs $PWD/*

echo ""
echo `date`
echo "---------------------------------------------------------------------------"
echo "FINISHED" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"

