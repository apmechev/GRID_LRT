#!/bin/bash

function setup_lofar_leiden(){
   source /net/para34/data1/oonk/lof_nov2016_2_19_0/lofim.sh
   echo "setup_env: Loaded LOFAR from /net/para34/data1/oonk/lof_nov2016_2_19_0/lofim.sh"
}

function setup_lofar_herts(){
  module load casa
  module load lofar
  source /soft/lofar-051116/lofarinit.sh
  export PYTHONPATH=/soft/pyrap:$PYTHONPATH
  echo "setup_env: Loaded LOFAR from /soft/lofar-051116/lofarinit.sh"
}


function setup_local_lofar(){
 case "$( hostname -f )" in
    *sara*) echo "setup_env: softdrive not found";exit 10;;
    *leiden*) setup_lofar_leiden ;;
    node[0-9]*) setup_lofar_herts;;
    *) echo "setup_env: Can't find host in list of supported clusters"; exit 12;;
 esac
}


function setup_softdrive_lofar(){
 export LD_LIBRARY_PATH=/cvmfs/softdrive.nl/apmechev/gcc-4.8.5/lib:/cvmfs/softdrive.nl/apmechev/gcc-4.8.5/lib64:$LD_LIBRARY_PATH
 if [ -z "$1" ]
  then
    echo "setup_env: Initializing default environment in /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16"
    . /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/init_env_release.sh
    export PYTHONPATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
    LOFAR_PATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/
  else
    if [ -e "$1/init_env_release.sh" ]; then
      echo "setup_env: Initializing environment from ${1}"
      . ${1}/init_env_release.sh
      export PYTHONPATH=${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
      export LOFARDATAROOT=/cvmfs/softdrive.nl/wjvriend/data
    else
        echo "setup_env: The environment script doesn't exist. check the path $1/init_env_release.sh again"
        exit 11 #exit 11=> no init_env script
    fi
  fi
}

function setup_LOFAR_env(){

 if [ ! -z $( echo $1 | grep cvmfs ) ]
  then
    if [ -d /cvmfs/softdrive.nl ]
     then
      echo "setup_enc: softdrive directory found"
      setup_softdrive_lofar $1
     else
      echo "setup_env: No Softdrive installation. Trying to source LOFAR otherwise"
      setup_local_lofar 

   fi
 fi
}

