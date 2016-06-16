#!/bin/bash

echo "Downloading Subbands "${1}" to "${2}" from file "${3}
for i in $(seq ${1} ${2}); do head -n $i ${3}|tail -n 1|  awk '{ print $1}' |xargs prefactor/bin/getfiles.sh &  echo $!" SB"$i>>activejobs; done #get line, get first column, execute as argument to getfiles.sh
