#!/bin/bash

#$1==output log
function process_output(){
 more $1
 if [[ $( grep "[E|e]xception" $1 ) > "" ]]
 then
     $OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'NDPPP_crashed!'
  if [[ $( grep "RegularFileIO" $1 ) > "" ]]
  then
        echo "NDPPP crashed because of bad download"
        exit 17 #exit 17=> Files not downloaded fully
   fi

   exit 99 #exit 99=> generic prefactor error
 fi


}
