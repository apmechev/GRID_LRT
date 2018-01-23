#!/bin/bash

function upload_results(){
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading_results'
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

 case "${PIPELINE}" in
    pref_cal1) upload_results_cal1 ;;
    pref_cal2) upload_results_cal2 ;;
    pref_targ1) upload_results_targ1 ;;
    pref_targ2) upload_results_targ2 ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac

}


function upload_results_cal1(){

 find ${RUNDIR} -name "instrument"
 find ${RUNDIR} -name "instrument" |xargs tar -cvf instruments_${OBSID}_${STARTSB}.tar  
 if [[ $? != 0 ]]; then
    echo "instrument files not found!"
    exit 99
 fi
 find ${RUNDIR} -iname "FIELD" |grep work |xargs tar -rvf instruments_${OBSID}_${STARTSB}.tar 
 find ${RUNDIR} -iname "ANTENNA" |grep work |xargs tar -rvf instruments_${OBSID}_${STARTSB}.tar

 uberftp -mkdir ${RESULTS_DIR}/${OBSID}
#export SSB=$(printf %03d ${STARTSB})
 globus-url-copy instruments_${OBSID}_${STARTSB}.tar ${RESULTS_DIR}/${OBSID}/${OBSID}_SB${STARTSB}.tar

}

function upload_results_cal2(){

  find ./prefactor/cal_results/ -name "*npy"|xargs tar -cf calib_solutions.tar
  find ./prefactor/results/ -iname "*h5" -exec tar -rvf calib_solutions.tar {} \;

  echo "Numpy files found:"
  find . -name "*npy"
  uberftp -mkdir ${RESULTS_DIR}/${OBSID}
  globus-url-copy file:`pwd`/calib_solutions.tar ${RESULTS_DIR}/${OBSID}/${OBSID}.tar
        wait
}


function upload_results_targ1(){

tar -zcvf results.tar.gz prefactor/results/L*
uberftp -mkdir ${RESULTS_DIR}/${OBSID}
globus-url-copy file:`pwd`/results.tar.gz ${RESULTS_DIR}/${OBSID}/${OBSID}_AB${A_SBN}.tar.gz
}

function upload_results_targ2(){

   uberftp -mkdir ${RESULTS_DIR}/${OBSID}
   globus-url-copy file:`pwd`/results.tar.gz ${RESULTS_DIR}/${OBSID}/${OBSID}_AB_${STARTSB}.tar.gz
    wait
}


function upload_results_from_token(){

echo ""

}
