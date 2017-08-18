#!/bin/bash

function upload_results(){
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'uploading_results'
echo "---------------------------------------------------------------------------"
echo "Copy the output from the Worker Node to the Grid Storage Element"
echo "---------------------------------------------------------------------------"

 case "${PIPELINE}" in
    ddf_image1) upload_results_ddf_image1 ;;
    ddf_image2) upload_results_ddf_image2 ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac

}


function upload_results_ddf_image1(){
 uberftp -mkdir ${RESULTS_DIR}/${OBSID}
 rm ddf-pipeline/pipeline.py
 tar -cf step1.tar $( ls L*.ms/*sols* *fits *npy *DicoModel *crossmatch* image_bootstrap_* image_* 2>/dev/null)
 globus-url-copy step1.tar ${RESULTS_DIR}/${OBSID}/step1.tar
}

function upload_results_ddf_image2(){
 rm -rf *cache *.ms
 echo "tarring targ2 results" 
  tar -cvf results.tar *fits
  ls -lath results.tar
  echo "Uploading results to"  ${RESULTS_DIR}/${OBSID}/step2.tar
  globus-url-copy results.tar ${RESULTS_DIR}/${OBSID}/step2.tar

}



function upload_results_from_token(){

echo ""

}
