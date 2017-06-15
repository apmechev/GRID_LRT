#!/bin/bash


function replace_dirs(){
 cp prefactor/pipeline.cfg . 
 sed -i "s?LOFAR_ROOT?${LOFAR_PATH}?g" pipeline.cfg
 echo  "replaced LOFAR_PATH in pipeline.cfg"



 sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" ${PARSET}
 sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" pipeline.cfg
 echo "Replacing "$PWD" in the prefactor parset"

 if [[ ! -z $( echo $PIPELINE |grep targ ) ]]
  then
   pipelinetype=$PIPELINE
  elif [[ ! -z $( echo $PARSET | grep Initial-Subtract ) ]]
   then
    pipelinetype="pref.insub"
  else
   pipelinetype="pref.cal"
 fi

 sed -i "s?sortmap_target\.argument\.firstSB.*=?sortmap_target\.argument\.firstSB    = ${STARTSB}?g" *parset

 echo "Pipeline type is "$pipelinetype
 echo "Adding $OBSID and $pipelinetype into the tcollector tags"
 sed -i "s?\[\]?\[\ \"obsid=${OBSID}\",\ \"pipeline=${pipelinetype}\"\]?g" tcollector/collectors/etc/config.py

}
