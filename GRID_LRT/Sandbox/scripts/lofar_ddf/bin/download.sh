#!/bin/bash

#First argument is file, second argument is $PIPELINE

function download_files(){
 echo "Downloading $(wc -l $1 | awk '{print $1}' ) files"
 $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'downloading'

 case "$2" in
    ddf_image1) echo "downloading files for first image step"; dl_img1 $1 ;;
    ddf_image2) echo "downloading files for second step"; dl_img1 $1; dl_img2 ;; 
    *) echo "Unsupported pipeline, nothing downloaded"; exit 20;;
 esac

}




function dl_img1(){
# Cool bash code that martin's less cool python code does
    while read p; do tt=$( echo $p |tr -d '\r'|tr -d '\n' ); globus-url-copy ${tt} ./ ; done < $1
    echo "Download complete, Extracting"
    ${OLD_PYTHON} set_token_field.py $TOKEN status extracting
    for i in `ls *tar.gz`; do tar -zxf $i & done
    wait
    echo "Extraction complete"

    rm -rf *tar.gz
    mv prefactor/results/* . 

    ${OLD_PYTHON} set_token_field.py $TOKEN status downloaded
}


function dl_img2(){
  ${OLD_PYTHON} set_token_field.py $TOKEN status "downloading_step_1_files"

  globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/ddf/ddf_image1/${OBSID}/step1.tar step1.tar
  echo "Downloaded step1 files"

  tar -xvf step1.tar
  rm -f step1.tar

  ${OLD_PYTHON} set_token_field.py $TOKEN status downloaded_step1
  touch temp_mslist.txt
}

