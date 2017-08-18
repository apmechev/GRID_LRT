#!/bin/bash


function print_info(){
echo  ""
echo  "-----------------------------------------------------------------------"
echo  "Obtain information for the Worker Node and set the LOFAR environment"
echo  "----------------------------------------------------------------------"

echo "-"
echo "w_info: hostname = "  $HOSTNAME
echo "w_info: homedir = " $HOME

echo "w_info: Job directory = " $PWD
ls -l $PWD

echo "-"
echo "w_info: WN Architecture is:"
cat /proc/meminfo | grep "MemTotal" |xargs echo "w_info: "
cat /proc/cpuinfo | grep "model name" |xargs echo "w_info: "

#CHECKING FREE DISKSPACE AND FREE MEMORY AT CURRENT TIME
echo ""
echo "w_info: current data and time = " $( date )
echo "w_info: free disk space = "
df -h . 
echo "w_info: free memory " 
free 
freespace=`stat --format "%a*%s/1024^3" -f $TMPDIR|bc`
echo "w_info: Free scratch space = "$freespace"GB"




echo "++++++++++++++++++++++++++++++"
echo "++++++++++++++++++++++++++++++"
echo  "var LOFARDATAROOT: " ${LOFARDATAROOT}
echo  "setup" "adding symbolic link for EPHEMERIDES and GEODETIC data into homedir"

echo "job info" "INITIALIZATION OF JOB ARGUMENTS"
echo "job info" ${JOBDIR}
echo "job info" ${OBSID}



echo ""
}
