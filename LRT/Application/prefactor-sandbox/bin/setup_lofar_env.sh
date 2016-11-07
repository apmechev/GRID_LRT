#!/bin/bash

function setup_LOFAR_env(){
export LD_LIBRARY_PATH=/cvmfs/softdrive.nl/apmechev/gcc-4.8.5/lib:/cvmfs/softdrive.nl/apmechev/gcc-4.8.5/lib64:$LD_LIBRARY_PATH
 if [ -z "$1" ]
  then
    echo "Initializing default environment"
    . /cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/init_env_release.sh
    export PYTHONPATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
  LOFAR_PATH=/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16/
  else
    if [ -e "$1/init_env_release.sh" ]; then
      echo "Initializing environment from ${1}"
      . ${1}/init_env_release.sh
      export PYTHONPATH=${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg:${1}/local/release/lib/python2.7/site-packages/losoto-1.0.0-py2.7.egg/losoto:$PYTHONPATH
      export LOFARDATAROOT=/cvmfs/softdrive.nl/wjvriend/data
    else
        echo "The environment script doesn't exist. check the path $1/init_env_release.sh again"
        exit 11 #exit 11=> no init_env script
    fi
  fi
}

