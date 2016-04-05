#!/bin/bash
export PATH=/cvmfs/softdrive.nl/apmechev/igprof/bin:$PATH
export LD_LIBRARY_PATH=/cvmfs/softdrive.nl/apmechev/igprof/lib


cd /home/apmechev/SARA_FAD/FAD_v7/Tokens
python removeObsIDTokens.py  L234028 spectroscopy_alex apmechev prQn98rQA
python createTokens.py  L234028 spectroscopy_alex apmechev prQn98rQA
cd -
./startpilot.sh spectroscopy_alex apmechev prQn98rQA


