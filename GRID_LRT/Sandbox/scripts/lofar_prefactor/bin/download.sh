#!/bin/bash

#First argument is file, second argument is $PIPELINE

function download_files(){
 echo "Downloading $(wc -l $1 | awk '{print $1}' ) files"
 $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'downloading'

 case "$2" in
    *cal1*) echo "downloading cal1 files"; dl_cal1 $1 ;;
    *cal2*) echo "downloading cal_solutions"; dl_cal2 $1 ;;
    *targ1*) echo "downloading target1 SB"; dl_cal1 $1  ;;
    *targ2*) echo "Downloading targ1 solutions";dl_targ2 $1 ;;
    *) echo "Unsupported pipeline, nothing downloaded"; exit 20;; #exit 20=> wrong pipeline
 esac

}

function dl_targ1(){

   $OLD_PYTHON  wait_for_dl.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD}
   python ./download_srms.py $1 0 $( wc -l $1 | awk '{print $1}' ) || { echo "Download Failed!!"; exit 21; } #exit 21=> Download fails
   for i in `ls *tar`; do tar -xvf $i &&rm $i; done 
 
}

function download(){
 dl_cal1 $1
}

function dl_cal1(){

   if [[ ! -z $( cat $1 | grep juelich )  ]]; then 
     sed -i 's?srm://lofar-srm.fz-juelich.de:8443?gsiftp://lofar-gridftp.fz-juelich.de:2811?g' $1  # xargs -I{} globus-url-copy -st 30 {} $PWD/ || { echo 'downloading failed' ; exit 20; }
   fi
   if [[ ! -z $( cat $1 | grep sara )  ]]; then
     sed -i 's?srm://srm.grid.sara.nl:8443?gsiftp://gridftp.grid.sara.nl:2811?g' $1 #| xargs -I{} globus-url-copy -st 30 {} $PWD/ || { echo 'downloading failed' ; exit 20; }
   fi
   while read line; do echo $line| globus-url-copy  $line ${PWD}/ || { echo 'downloading failed' ; exit 21;  } ; done < $1
   wait
   for i in `ls *tar`; do tar -xf $i && rm -rf $i; done
   for i in `ls *gz`; do tar -zxf $i && rm -rf $i; done
}

function dl_cal2(){

   sed 's?srm://srm.grid.sara.nl:8443?gsiftp://gridftp.grid.sara.nl:2811?g' $1 | xargs -I{} globus-url-copy -st 30 {} $PWD/ || { echo 'downloading failed' ; exit 21; }
   for i in `ls *tar`; do tar -xf $i &&rm $i; done
   find . -name "${OBSID}*ndppp_prep_cal" -exec mv {} . \;   

}

function dl_targ2(){

   cat $1 | xargs -I{} globus-url-copy  {} $PWD/ || { echo 'downloading failed' ; exit 21;  } 
   for i in `ls *gz`; do tar -zxf $i; done
   mv prefactor/results/L* ${RUNDIR}

}

 
