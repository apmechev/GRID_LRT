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

   if [[ $SURL == *sara* ]]; then
      TURL=`echo $SURL | sed -e "s%${sara_SURL_string}%${sara_TURL_string}%g"`
   elif [[ $SURL == *juelich* ]]; then
      TURL=`echo $SURL | sed -e "s%${juelich_SURL_string}%${juelich_TURL_string}%g"`
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

#LOFARROOT=${VO_LOFAR_SW_DIR}/LTA_2_1/lofar/release
LOFARROOT=${VO_LOFAR_SW_DIR}/current/lofar/release

echo "source lofarinit.sh"
#. ${VO_LOFAR_SW_DIR}/LTA_2_1/lofar/release/lofarinit.sh || exit 1
. ${VO_LOFAR_SW_DIR}/current/lofar/release/lofarinit.sh || exit 1

echo "correct PATH and LD_LIBRARY_PATH for incomplete settings in lofarinit.sh"
# initialize the Lofar LTA environment; release LTA_2_1
#export PATH=$VO_LOFAR_SW_DIR/LTA_2_1/lofar/release/bin:$VO_LOFAR_SW_DIR/LTA_2_1/lofar/release/sbin:$VO_LOFAR_SW_DIR/LTA_2_1/local/release/bin:$PATH
#export LD_LIBRARY_PATH=$VO_LOFAR_SW_DIR/LTA_2_1/lofar/release/lib:$VO_LOFAR_SW_DIR/LTA_2_1/lofar/release/lib64:$VO_LOFAR_SW_DIR/LTA_2_1/local/release/lib:$VO_LOFAR_SW_DIR/LTA_2_1/local/release/lib64:$LD_LIBRARY_PATH
#export PYTHONPATH=$VO_LOFAR_SW_DIR/LTA_2_1/lofar/release/lib/python2.7/site-packages:$VO_LOFAR_SW_DIR/LTA_2_1/local/release/lib/python2.7/site-packages:$PYTHONPATH
export PATH=$VO_LOFAR_SW_DIR/current/lofar/release/bin:$VO_LOFAR_SW_DIR/current/lofar/release/sbin:$VO_LOFAR_SW_DIR/current/local/release/bin:$PATH
export LD_LIBRARY_PATH=$VO_LOFAR_SW_DIR/current/lofar/release/lib:$VO_LOFAR_SW_DIR/current/lofar/release/lib64:$VO_LOFAR_SW_DIR/current/local/release/lib:$VO_LOFA
R_SW_DIR/current/local/release/lib64:$LD_LIBRARY_PATH
export PYTHONPATH=$VO_LOFAR_SW_DIR/current/lofar/release/lib/python2.7/site-packages:$VO_LOFAR_SW_DIR/current/local/release/lib/python2.7/site-packages:$PYTHONPAT
H

# NB we can't assume the home dir is shared across all Grid nodes.
echo "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"
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
echo "untar scripts"
tar -xf scripts.tar
cp -r scripts/* .

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
free -h





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
snt=`echo ${SURL_SUBBAND} | cut -d'/' -f 12`
sn1=`echo ${snt} | cut -d'_' -f 1` #obsid
sn2=`echo ${snt} | cut -d'_' -f 2` #subband
sn3=`echo ${snt} | cut -d'_' -f 3` #uv extension (uv.dppp.MS)
sn4=`echo ${snt} | cut -d'_' -f 4` #uniq srm extension
untarred_name=${sn1}_${sn2}_${sn3}_${sn4}
echo "untarred surl file: ", $untarred_name
new_name=${sn1}_${sn2}_${sn3}
echo "desired file name : ", $new_name
#
#use also the subband number for srm storage of output .fa files
sbn=${sn2}
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
#sbn=${SUBBAND_NUM}
echo $path


# EXECUTE PYTHON PROCESSING
echo ""
echo "execute avg_dmx.py"
#time python avg_dmx.py $path $avg_freq_step $avg_time_step $do_demix $demix_freq_step $demix_time_step $demix_sources $select_nl > log_$name
#time python avg_dmx_v2.py $name $avg_freq_step $avg_time_step $do_demix $demix_freq_step $demix_time_step $demix_sources $select_nl > log_$name
time python avg_dmx_v2C.py $name $avg_freq_step $avg_time_step $do_demix $demix_freq_step $demix_time_step $demix_sources $select_nl > log_$name 2>&1
echo "Done Command: "
echo "time python avg_dmx_v2.py", $name, $avg_freq_step, $avg_time_step, $do_demix, $demix_freq_step, $demix_time_step, $demix_sources, $select_nl
#
# - step3 finished check contents
echo "step3 finished, list contents"
ls -l $PWD
du -hs $PWD
du -hs $PWD/*

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
   echo ".FA FILES do not exist. Clean up and Exit now..."
   cp log_$name ${JOBDIR}
   cd ${JOBDIR}
   rm -rf ${RUNDIR}
   exit 1
fi

echo "Tarring .fa files: "${name}".fa"
#tar -cvf ${name}.fa.tar *.fa > logtar_${name}.fa
tar -czvf ${name}.fa.tgz *.fa *.parset log_* > logtar_${name}.fa
echo "Copy output to the Grid SE"
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
   rm -rf ${RUNDIR}
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
rm -rf ${RUNDIR} 
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