#!/bin/bash

function cleanup(){
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
}


