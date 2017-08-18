#!/bin/bash

#First argument is file, second argument is $PIPELINE

function download_files(){
 echo "Downloading $(wc -l $1 | awk '{print $1}' ) files"
 $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'downloading'

 case "$2" in
    ndppp_cal) echo "downloading calibrator files"; dl_cal $1 ;;
    ndppp_targ) echo "downloading target1 SB"; dl_targ $1  ;;
    *) echo "Unsupported pipeline, nothing downloaded"; exit 20;;
 esac

}




function dl_targ(){
   $OLD_PYTHON  wait_for_dl.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD}
   python ./download_srms.py $1 0 $( wc -l $1 | awk '{print $1}' ) || { echo "Download Failed!!"; exit 20; } #exit 20=> Download fails
   for i in `ls *tar`; do tar -xvf $i &&rm $i; done 
 
}

function dl_cal(){
   if [[ ! -z $( cat $1 | grep juelich )  ]]; then 
     sed 's?srm://lofar-srm.fz-juelich.de:8443?gsiftp://lofar-gridftp.fz-juelich.de:2811?g' $1 | xargs -I{} globus-url-copy -st 30 {} $PWD/ || { echo 'downloading failed' ; exit 20; }
   fi
   if [[ ! -z $( cat $1 | grep sara )  ]]; then
     sed 's?srm://srm.grid.sara.nl:8443?gsiftp://gridftp.grid.sara.nl:2811?g' $1 | xargs -I{} globus-url-copy -st 30 {} $PWD/ || { echo 'downloading failed' ; exit 20; }
   fi
   wait
   for i in `ls *tar`; do tar -xf $i && rm -rf $i; done
}

