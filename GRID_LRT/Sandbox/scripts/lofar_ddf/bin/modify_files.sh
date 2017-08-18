#!/bin/bash


function replace_dirs(){

 sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" ${PARSET}
 sed -i "s?PREFACTOR_SCRATCH_DIR?$(pwd)?g" parset.cfg
 echo "Replacing "$PWD" in the prefactor parset"
 if [[ ! -z $( echo $PIPELINE |grep image1 ) ]]
  then
   sed -i '445s/.*/    sys.exit()/' ddf-pipeline/pipeline.py
 fi
 export pipelinetype=$PIPELINE

 echo "Pipeline type is "$pipelinetype
 echo "Adding $OBSID and $pipelinetype into the tcollector tags"
 sed -i "s?\[\]?\[\ \"obsid=${OBSID}\",\ \"pipeline=${pipelinetype}\"\]?g" tcollector/collectors/etc/config.py

}
