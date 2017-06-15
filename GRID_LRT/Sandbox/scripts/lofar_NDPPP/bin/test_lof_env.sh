#!/bin/bash

function test_lofar_env(){
source setup_lofar_env.sh

setup_LOFAR_env /cvmfs/softdrive.nl/apmechev/lofar_prof/2_18 
echo $PYTHONPATH
echo $PATH
}
