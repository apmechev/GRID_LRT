#!/bin/bash

function download_cals(){

 echo "Getting solutions from obsid " $1
 globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_cal2/${1}_solutions.tar file:`pwd`/cal_solutions.tar
 wait
 if [[ -e cal_solutions.tar ]]
  then
    tar -xvf cal_solutions.tar
 else
    exit 31 #exit 31=> numpy solutions do not get downloaded
 fi

}
