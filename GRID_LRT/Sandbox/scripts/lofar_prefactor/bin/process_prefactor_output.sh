#!/bin/bash

#$1==output log
function process_output(){
 if [[ ! -f $1 ]]; then
    echo  "output file not produced!"
    exit 90 # exit 90 => No output file exists
 fi
 more $1
 if [[ $( grep "finished unsuccesfully" $1 ) > "" ]]
 then
     $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'prefactor_crashed!'
     echo "Pipeline did not finish, tarring work and run directories for re-run"
     RERUN_FILE=$OBSID"_"$STARTSB"prefactor_error.tar"
     echo "Will be  at gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/error_states"$RERUN_FILE
#     tar -cf $RERUN_FILE prefactor/
#     globus-url-copy file:`pwd`/$RERUN_FILE gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/error_states/$RERUN_FILE
   if [[ $(hostname -s) != 'loui' ]]; then
    echo "removing RunDir"
    rm -rf ${RUNDIR}
   fi
   if [[ $( grep "bad_alloc" $1 ) > "" ]]
   then
        echo "Prefactor crashed because of bad_alloc. Not enough memory"
        exit 98 #exit 98=> Bad_alloc error in prefactor
   fi
   if [[ $( grep "-9" $1 ) > "" ]]
   then
        echo "Prefactor crashed because of dppp: Not enough memory"
        exit 97 #exit 97=> dppp memory error in prefactor
   fi

   if [[ $( grep "RegularFileIO" $1 ) > "" ]]
   then
        echo "Prefactor crashed because of bad download"
        exit 96 #exit 96=> Files not downloaded fully
   fi

   exit 99 #exit 99=> generic prefactor error
 fi


}
