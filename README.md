# SARA_FAD 

The SurfSARA Flagging, Averaging Demixing pipeline is an automated framework able to submit preprocessing jobs on the SARA Grid. The job submission gives the user both simplicity and flexibility, by allowing a quick default run on a data list as well as the ability to provide a custom user defined parameter set(parset). 

For minimal setup, the user only needs to specify a list of surls where the data is located and run the script with the master_setup.cfg. Alternatively, the user may specify a custom set of steps/parameters placed in FAD_v7/parsets and add it to the setup file such as custom_setup.cfg

Currently Implemented:
user defined parsets in /FADv7/parsets
.cfg file can specify parset to run
scripts to modify the parset on the node (inputfile_script.py)

In Development:
gaincal
profiling CPU/MEM/IO usage
aoflag crash (??)
more parset modification scripts

Next:
losoto integration
selecting LOFAR Stack version
improved error reporting

