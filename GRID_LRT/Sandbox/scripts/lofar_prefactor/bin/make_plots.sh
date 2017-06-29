#!/bin/bash

function make_pie(){

xmlfile=$( find . -name "*statistics.xml" 2>/dev/null)
#cp piechart/autopie.py .
./autopie.py ${xmlfile} PIE_${OBSID}_${PIPELINE}.png
cp $! ${WORKDIR}

}

function make_plots(){

if [[ ! -z $( echo $pipelinetype |grep targ2 ) ]]
  then
    ./prefactor/scripts/plot_solutions_all_stations.py -p $( ls -d ${RUNDIR}/prefactor/results/*ms )/instrument_directionindependent/ ${JOBDIR}/GSM_CAL_${OBSID}_ABN${STARTSB}_plot.png
fi

xmlfile=$( find . -name "*statistics.xml" 2>/dev/null)
cp piechart/autopie.py .
./autopie.py ${xmlfile} PIE_${OBSID}.png

find . -name "PIE*png"|xargs tar -zcf pngs.tar.gz
find . -name "*.png" -exec cp {} ${JOBDIR} \;
cp PIE_${OBSID}.png ${JOBDIR}
cp ./prefactor/cal_results/*png ${JOBDIR}

}

