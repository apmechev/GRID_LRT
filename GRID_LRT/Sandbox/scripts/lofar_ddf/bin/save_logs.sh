#!/bin/bash

function tarlogs(){
# find . -iname "*statistics.xml" -exec tar -rvf profile.tar {} \;
# find . -name "*png" -exec tar -rvf profile.tar {} \;
# tar --append --file=profile.tar output

 case "${PIPELINE}" in
    pref_cal1) echo "" ;;
    pref_cal2) tar_logs_cal2 ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac

}


function tar_logs_cal2(){

find ./prefactor/cal_results/ -name "*npy"|xargs tar -cf calib_solutions.tar
find ./prefactor/results/ -iname "*h5" -exec tar -rvf calib_solutions.tar {} \;

echo "Numpy files found:"
find . -name "*npy"


}
