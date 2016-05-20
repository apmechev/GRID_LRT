#!/bin/bash


#####Get list of surls and copy them to the node: Use a FIFO

#TODO:Loop over files in srmlist


# Create fifo for input file on SRM to use the minimal local scratch space on the Worker Node
mkfifo ${INPUT_FIFO}
# Extract input data from input file (fifo) and catch PID
tar -Bxf ${INPUT_FIFO} & TAR_PID=$!
echo "download file"
# The untar from fifo has started, so now start download into fifo
time globus-url-copy ${TURL_SUBBAND} file:///`pwd`/${INPUT_FIFO} && wait $TAR_PID
# At this point, if globus-url-copy fails it will generate a non-zero exit status. If globus-url-copy succeeds it will execute the wait for $TAR_PID, which will generate the exit status of the tar command. This means that, at this point, the exit status will only be zero when both the globus-url-copy and the tar commands finished succesfully.
# Exit loop on non-zero exit status:
if [[ "$?" != "0" ]]; then
   echo "Problem fifo copy files. Clean up and Exit now..."
   cd ${JOBDIR}
   rm -rf ${RUNDIR}
   exit 1
fi



#####

