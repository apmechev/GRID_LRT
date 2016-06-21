#!/bin/bash

##Shell file that is run on the node to call and unzip the requested SURLS as requested by the User
#Currently this only does one file taken as an argument. Thinking of how to do a list of files


SURL_SUBBAND=${1}
SURLtoTURL()
{
   SURL=${1}
   sara_TURL_string="gsiftp://gridftp.grid.sara.nl:2811"
   sara_SURL_string="srm://srm.grid.sara.nl:8443"
   juelich_TURL_string="gsiftp://dcachepool12.fz-juelich.de:2811"
   juelich_SURL_string="srm://lofar-srm.fz-juelich.de:8443"

   if [[ $SURL == *sara* ]]; then
      TURL=`echo $SURL | sed -e "s%${sara_SURL_string}%${sara_TURL_string}%g"`
   elif [[ $SURL == *juelich* ]]; then
      TURL=`echo $SURL | sed -e "s%${juelich_SURL_string}%${juelich_TURL_string}%g"`
   fi

   echo $TURL
}



#OUTPUT_FIFO="GRID_output_fifo.tar" #for large size output
TURL_SUBBAND=$( SURLtoTURL ${SURL_SUBBAND} )
SBN=$(echo $TURL_SUBBAND | sed 's/.*_\(SB[0-9][0-9][0-9]\)_.*/\1/')
INPUT_FIFO="GRID_input_fifo-"$SBN".tar"

# create a temporary working directory
#RUNDIR=`mktemp -d -p $TMPDIR`
#cp $PWD/scripts.tar $RUNDIR
#cp $PWD/prefactor.tar $RUNDIR
#cd ${RUNDIR}
#echo "untar scripts, parsets!!"
#tar -xvf scripts.tar
#tar -xvf prefactor.tar
#cp -r scripts/* .


full_surl=${SURL_SUBBAND}

echo "create fifo for input "$SBN
# Fifo solution based on a trick by Coen.Schrijvers@surfsara.nl:
# Create fifo for input file on SRM to use the minimal local scratch space on the Worker Node
mkfifo ${INPUT_FIFO}
# Extract input data from input file (fifo) and catch PID
tar -Bxf ${INPUT_FIFO} & TAR_PID=$!
## The untar from fifo has started, so now start download into fifo
time globus-url-copy ${TURL_SUBBAND} file:///`pwd`/${INPUT_FIFO} && wait $TAR_PID 
# At this point, if globus-url-copy fails it will generate a non-zero exit status. If globus-url-copy succeeds it will execute the wait for $TAR_PID, which will generate the exit status of the tar command. This means that, at this point, the exit status will only be zero when both the globus-url-copy and the tar commands finished succesfully.
# Exit loop on non-zero e::w
#exit status:
if [[ "$?" != "0" ]]; then
   echo "Problem fifo copy files"$SBN". Clean up and Exit now..."
   cd ${JOBDIR}
   rm -rf ${RUNDIR}
########   exit 1
fi
# Continue loop if copy succeeded

echo "remove fifo for subband"$SBN
rm -f ${INPUT_FIFO}
#


##
#Now check for folders that are too small:
##
##du -hs L342934_SB*/ | grep -v 248M | awk '{print $2}'
