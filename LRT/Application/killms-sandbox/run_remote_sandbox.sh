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
#tar -xf picas.tar
#tar -xf couchdb.tar
git clone https://github.com/apmechev/GRID_picastools.git p_tools_git
mv p_tools_git/* . 
rm -rf p_tools_git/


python getOBSID.py $1 $2 $3 
echo "Pulling down the sandbox for OBSID "$OBSID" from /pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_$2_$OBSID.tar"





uberftp -rm gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_$1_$OBSID.tar
ls -l

# Start the pilot jobs by contacting PiCaS tokens



