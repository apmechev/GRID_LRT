#!/bin/bash


function print_info(){
echo  ""
echo  "-----------------------------------------------------------------------"
echo  "Obtain information for the Worker Node and set the LOFAR environment"
echo  "----------------------------------------------------------------------"

echo "-"
echo "worker info" `date`
echo "worker info"  $HOSTNAME
echo "worker info" $HOME

echo "worker info" "-"
echo "worker info" "Job directory is:"
echo "worker info" $PWD
ls -l $PWD

echo "-"
echo "worker info" "WN Architecture is:"
cat /proc/meminfo | grep "MemTotal"
cat /proc/cpuinfo | grep "model name"


# initialize job arguments
# - note, obsid is only used to store the data


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



echo "++++++++++++++++++++++++++++++"
echo "++++++++++++++++++++++++++++++"



}
