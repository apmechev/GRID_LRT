#!/bin/bash

# ===================================================================== #
# authors: Natalie Danezi <anatoli.danezi@surfsara.nl>  --  SURFsara    #
#          J.B.R. Oonk <oonk@strw.leidenuniv.nl>    -- Leiden/ASTRON    #
#                                                                       #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: ./master_avg_dmx.sh [OBSID] [SURL_SUBBAND]                     #
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

SURLtoTURL()
{
   SURL=${1}
   sara_TURL_string="gsiftp://gridftp.grid.sara.nl:2811"
   sara_SURL_string="srm://srm.grid.sara.nl:8443"
   juelich_TURL_string="gsiftp://dcachepool12.fz-juelich.de:2811"
   juelich_SURL_string="srm://lofar-srm.fz-juelich.de:8443"
   #poznan_TURL_string="gsiftp://door01.lofar.psnc.pl:2811"
   poznan_TURL_string="gsiftp://door02.lofar.psnc.pl:2811"
   poznan_SURL_string="srm://lta-head.lofar.psnc.pl:8443"

   if [[ $SURL == *sara* ]]; then
      TURL=`echo $SURL | sed -e "s%${sara_SURL_string}%${sara_TURL_string}%g"`
   elif [[ $SURL == *juelich* ]]; then
      TURL=`echo $SURL | sed -e "s%${juelich_SURL_string}%${juelich_TURL_string}%g"`
   elif [[ $SURL == *psnc* ]]; then 
      TURL=`echo $SURL | sed -e "s%${poznan_SURL_string}%${poznan_TURL_string}%g"`
      export GLOBUS_TCP_PORT_RANGE=20000,25000
   fi

   echo $TURL
}

set -x
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

echo ""
echo "Setting up the LOFAR environment; release current:"

SW_BASE_DIR=/cvmfs/softdrive.nl/wjvriend/lofar_stack/
#LOFARROOT=${VO_LOFAR_SW_DIR}/LTA_2_1/lofar/release
LOFARROOT=${SW_BASE_DIR}/2.16/current/lofar/release

echo "source lofarinit.sh"
#. ${VO_LOFAR_SW_DIR}/LTA_2_1/lofar/release/lofarinit.sh || exit 1
#. ${SW_DIR}/current/lofar/release/lofarinit.sh || exit 1
. $SW_BASE_DIR/2.16/init_env_release.sh

# NEW NB we can't assume the home dir is shared across all Grid nodes.
echo ""
echo "LOFARDATAROOT: ", ${LOFARDATAROOT}
echo "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"


echo "correct PATH and LD_LIBRARY_PATH for incomplete settings in lofarinit.sh"
# initialize the Lofar LTA environment; release LTA_2_1
#export PATH=$SW_DIR/current/lofar/release/bin:$SW_DIR/current/lofar/release/sbin:$SW_DIR/current/local/release/bin:$PATH
#export LD_LIBRARY_PATH=$SW_DIR/current/lofar/release/lib:$SW_DIR/current/lofar/release/lib64:$SW_DIR/current/local/release/lib:$SW_DIR/current/local/release/lib64:$LD_LIBRARY_PATH
#export PYTHONPATH=$SW_DIR/current/lofar/release/lib/python2.7/site-packages:$SW_DIR/current/local/release/lib/python2.7/site-packages:$PYTHONPATH

# NB we can't assume the home dir is shared across all Grid nodes.
#echo "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"
ln -s $VO_LOFAR_SW_DIR/data ~/


# initialize job arguments
# - note, obsid is only used to store the data
JOBDIR=${PWD}
OBSID=${1}
SURL_SUBBAND=${2}
AVG_FREQ_STEP=${3}
AVG_TIME_STEP=${4}
DO_DEMIX=${5}
DEMIX_FREQ_STEP=${6}
DEMIX_TIME_STEP=${7}
DEMIX_SOURCES=${8}
SELECT_NL=${9}
SUBBAND_NUM=${10}
PARSET=${11}
echo "++++++++++++++++++++++++++++++"
echo $PARSET
echo "++++++++++++++++++++++++++++++"

echo "INITIALIZATION OF JOB ARGUMENTS"
echo ${JOBDIR}
echo ${OBSID}
echo ${SURL_SUBBAND}
echo ${AVG_FREQ_STEP}
echo ${AVG_TIME_STEP}
echo ${DO_DEMIX}
echo ${DEMIX_FREQ_STEP}
echo ${DEMIX_TIME_STEP}
echo ${DEMIX_SOURCES}
echo ${SELECT_NL}
echo ${SUBBAND_NUM}
echo ""

INPUT_FIFO="GRID_input_fifo.tar"
#OUTPUT_FIFO="GRID_output_fifo.tar" #for large size output
TURL_SUBBAND=$( SURLtoTURL ${SURL_SUBBAND} )

# create a temporary working directory
RUNDIR=`mktemp -d -p $TMPDIR`
cp $PWD/scripts.tar $RUNDIR
cd ${RUNDIR}
echo "untar scripts, parsets!!"
tar -xvf scripts.tar
cp -r scripts/* .
ls -lat parsets/
ls -lat 
pwd

echo ""
echo "---------------------------------------------------------------------------"
echo "START PROCESSING" $OBSID "SUBBAND:" $SURL_SUBBAND
echo "---------------------------------------------------------------------------"

#NEED TO EXTRACT MS NAME FROM SURL
full_surl=${SURL_SUBBAND}

#CHECKING FREE DISKSPACE AND FREE MEMORY AT CURRENT TIME
echo ""
echo "current data and time"
date
echo "free disk space"
df -h .
echo "free memory"
free 



#STEP2
echo ""
echo "---------------------------"
echo "START AVG DMX"
echo "---------------------------"
echo "create fifo for input"
# Fifo solution based on a trick by Coen.Schrijvers@surfsara.nl:
# Create fifo for input file on SRM to use the minimal local scratch space on the Worker Node
mkfifo ${INPUT_FIFO}
# Extract input data from input file (fifo) and catch PID
tar -Bxf ${INPUT_FIFO} & TAR_PID=$!
echo "download file"
# The untar from fifo has started, so now start download into fifo
time globus-url-copy ${TURL_SUBBAND} file:///`pwd`/${INPUT_FIFO} && wait $TAR_PID
# At this point, if globus-url-copy fails it will generate a non-zero exit status. If globus-url-copy succeeds it will execute the wait for $TAR_PID, which will generate the exit status of the tar command. This means that, at this point, the exit status will only be zero when both the globus-url-copy and the tar commands finished succesfully.
# Exit loop on non-zero exit status:
if [[ "$?" != "0" ]]; then
   echo "Problem fifo copy files. Clean up and Exit now..."
   cd ${JOBDIR}
   rm -rf ${RUNDIR}
   exit 1
fi
# Continue loop if copy succeeded
echo "remove fifo"
rm -f ${INPUT_FIFO}
#
# - step2 finished check contents
echo "step2 finished, list contents"
ls -l $PWD
du -hs $PWD
du -hs $PWD/*

# STEP3 PYTHON PROCESSING PART
#
# get filename to be processed from surl

echo "Surl subband is"
echo {$SURL_SUBBAND}
SURL_SUBBAND=` ls -lat |grep L[0-9]* | awk '{print $(NF)}'`
if echo ${SURL_SUBBAND} | grep SAP
then
new_name=$(echo $SURL_SUBBAND |sed 's/\(L[0-9]*\)_\(SAP[0-9][0-9][0-9]\)_\(SB[0-9][0-9][0-9]\)_uv\.MS_[a-z0-9]*.tar/\1_\2_\3_uv\.MS\.tar/') 
echo "raw data"
elif echo $SURL_SUBBAND | grep dppp
then
new_name=$(echo $SURL_SUBBAND |sed 's/.*\(L[0-9]*\)_\(SB[0-9][0-9][0-9]\)_uv\.dppp\.MS_[a-z0-9]*.tar/\1_\2_uv\.MS\.tar/')
echo "dppp data"
else
echo "Can't process filename!!"
fi

untarred_name=${SURL_SUBBAND} #${sn1}_${sn2}_${sn3}_${sn4}
#untarred_name= ` ls -lat |grep L[0-9]* | awk '{print $(NF)}'`
echo "untarred surl file: ", $untarred_name
#new_name=${sn1}_${sn2}_${sn3}
echo "desired file name : ", $new_name
#
#use also the subband number for srm storage of output .fa files
sbn=$(echo $new_name | sed 's/.*_\(SB[0-9][0-9][0-9]\)_.*/\1/')
echo "sbn from sn2 : ", $sbn 

# NOT SURE IF RENAMING IS NECESSARY (WILL THE ABOVE COPY JOB REMOVE THE UNIQ SRM EXTENSION ?)
# rename L400139_SB000_uv.dppp.MS_13755198.tar -> L400139_SB000_uv.dppp.MS.tar from surl
#  surl example  srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc4_034/400139/L400139_SB000_uv.dppp.MS_13755198.tar
#  assume that after copy and fifo untar we have L400139_SB000_uv.dppp.MS_13755198 locally
#
# -----------------------------------------------------------
#
# ONLY DO THIS IF UNIQ SRM EXTENSION (PART AFTER .MS) IS NOT REMOVED BY ABOVE
# - should we add some checks here for file existence ?
echo ""
echo "rename untarred surl file: ", $untarred_name
mv $untarred_name $new_name
echo "Done Rename to create: ", $new_name
# -----------------------------------------------------------
#
# - step3 mv file done check contents
echo "step3 mv file done, list contents"
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

echo $path


# EXECUTE PYTHON PROCESSING
echo ""
echo "execute avg_dmx.py"

echo "parset is" $parset
if [[ -e "customscript.py" ]]; then
        echo "Executing custom avg_dmx script"
        time python customscript.py $name $avg_freq_step $avg_time_step $do_demix $demix_freq_step $demix_time_step $demix_sources $select_nl $parset > log_$name 2>&1
else
        time python avg_dmx_v2_noTS.py $name $avg_freq_step $avg_time_step $do_demix $demix_freq_step $demix_time_step $demix_sources $select_nl $parset > log_$name 2>&1
fi


echo "Done Command: "
echo "time python avg_dmx_v2.py", $name, $avg_freq_step, $avg_time_step, $do_demix, $demix_freq_step, $demix_time_step, $demix_sources, $select_nl
#
# - step3 finished check contents
echo "step3 finished, list contents"
ls -l $PWD
du -hs $PWD
du -hs $PWD/*

echo "::::parsetfile run:::::"
more *.parset*
#python log contents
echo "python run log contents"
more log_$name


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

# ADD A CHECK TO SEE IF *.fa FILES EXIST FIRST --> this ensures that we have the output available)
if [[ `ls -d *.fa | wc -l` < 1 ]]; then
   cat log_$name 
   echo ".FA FILES do not exist. Clean up and Exit now..."
   more *.parset*
   more log_$name
   cp log_$name ${JOBDIR}
   cd ${JOBDIR}

   if [[ $(hostname -s) != 'loui' ]]; then
      echo "removing RunDir"
      rm -rf ${RUNDIR} 
   fi
   exit 1
fi

echo "Tarring .fa files: "${name}".fa"
#tar -cvf ${name}.fa.tar *.fa > logtar_${name}.fa
tar -czvf ${name}.fa.tgz *.fa *.parset log_* > logtar_${name}.fa
echo "Copy output to the Grid SE"
echo ${OBSID}_${sbn}


if echo ${SURL_SUBBAND} | grep SAP; then
OBSID=$(echo $SURL_SUBBAND |sed 's/\(L[0-9]*\)_\(SAP[0-9][0-9][0-9]\)_\(SB[0-9][0-9][0-9]\)_uv\.MS_[a-z0-9]*.tar/\1_\2_\3_uv\.MS\.tar/'| cat $OBSID -)
fi
echo ${OBSID}_${sbn}
#
#srmrm srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}/${name}.fa.tar
#srmrm srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}/${name}.fa.tgz
#srmrmdir -recursive srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
#srmmkdir srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
#lcg-cp --vo lofar file:`pwd`/${name}.fs.msc.img.tar srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}/${name}.fa.tar
#lcg-cp --vo lofar file:`pwd`/${name}.fa.tgz srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}/${name}.fa.tgz
# remove any old existing directory from the Grid storage
uberftp -rm -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
# create the output directory on the Grid storage
uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}
# copy the output tarball to the Grid storage
globus-url-copy file:`pwd`/${name}.fa.tgz gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/${OBSID}_${sbn}/${name}.fa.tgz
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
echo "listing final files in scratch"
ls -allh $PWD
echo ""
du -hs $PWD
du -hs $PWD/*

echo ""
echo "copy logs to the Job home directory and clean temp files in scratch"
cp log_$name logtar_$name.fa ${JOBDIR}
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
