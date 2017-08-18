#!/bin/bash

function cleanup(){
if [[ "$?" != "0" ]]; then
   echo "Problem copying final files to the Grid. Clean up and Exit now..."
   cp log_$name logtar_$name.fa ${JOBDIR}
   cd ${JOBDIR}

   if [[ $(hostname -s) != 'loui' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR}
   fi
   exit 21 #exit 21=> cannot upload final files
fi
echo ""

echo ""
echo "copy echos to the Job home directory and clean temp files in scratch"
cp out* ${JOBDIR}
cp pngs.tar.gz ${JOBDIR}
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
}


