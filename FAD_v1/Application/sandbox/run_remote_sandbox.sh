# ===================================================================== #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara	#
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara	#
#                                                     		        #
# usage: . startpilot.sh [picas_db_name] [picas_username] [picas_pwd]	#
# description: Set PiCaS environment for the communication with couchDB #
#	       and start the pilot job                                  #
#                                                                       #
#          J.B.R. Oonk <oonk@strw.leidenuniv.nl>    -- Leiden/ASTRON    #
#          - dec 2015 updated this for FAD by JBRO                      #
#                                                                       #
# ===================================================================== #

set -x
tar -xf picas.tar
tar -xf couchdb.tar

OBSID=$(python getOBSID.py $1 $2 $3 |tail -1)
echo "Pulling down the sandbox for OBSID "$OBSID" from /pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_$1_$OBSID.tar"

globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_$1_$OBSID.tar file:`pwd`/sandbox.tar
tar -xf sandbox.tar

mv sandbox/* . 
rm -rf sandbox*.tar
rm -rf sandbox/
tar -xf picas.tar
tar -xf couchdb.tar

# Set permissions for the master script
chmod u+x master*.sh
uberftp -rm gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_$1_$OBSID.tar
ls -l

# Start the pilot jobs by contacting PiCaS tokens

python pilot.py $1 $2 $3 > pilot.log

