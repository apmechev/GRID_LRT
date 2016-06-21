#!/bin/bash

echo "Downloading Subbands "${1}" to "${2}" from file "${3}
for i in $(seq ${1} ${2}); do 

  srmfile=$(head -n $i ${3}|tail -n 1|  awk '{ print $1}')
  prefactor/bin/getfiles.sh $srmfile &  
  srmloc=$(echo $srmfile | sed 's/.*\(L[0-9]*\)_\(SB[0-9][0-9][0-9]\)_.*/\1_\2/' | awk '{print $1"_uv.dppp.MS"}' )
  echo $!" "$srmloc" 0">>activejobs; done #get line, get first column, execute as argument to getfiles.sh
