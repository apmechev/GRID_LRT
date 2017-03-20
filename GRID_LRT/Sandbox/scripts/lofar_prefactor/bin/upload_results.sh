#!/bin/bash

function upload_results(){
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading_results'
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

 case "${PIPELINE}" in
    pref_cal1) upload_results_cal1 ;;
    pref_cal2) upload_results_cal2 ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac

}


function upload_results_cal1(){
 find ${RUNDIR} -name "instrument" |xargs tar -cvf instruments_${OBSID}_${STARTSB}.tar  
 find ${RUNDIR} -iname "FIELD" |grep work |xargs tar -rvf instruments_${OBSID}_${STARTSB}.tar 
 find ${RUNDIR} -iname "ANTENNA" |grep work |xargs tar -rvf instruments_${OBSID}_${STARTSB}.tar

 uberftp -mkdir gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_tables/${OBSID}
 export OBSID=$(printf %03d ${OBSID})
 globus-url-copy instruments_${OBSID}_${STARTSB}.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_tables/${OBSID}/instruments_${OBSID}_${STARTSB}.tar

}

function upload_results_cal2(){

         globus-url-copy file:`pwd`/calib_solutions.tar gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_sols/${OBSID}_solutions.tar
        wait
}



function upload_results_from_token(){

echo ""

}
