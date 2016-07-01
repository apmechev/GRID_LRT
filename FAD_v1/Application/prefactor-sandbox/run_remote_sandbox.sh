# ===================================================================== #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara    #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: . startpilot.sh [picas_db_name] [picas_username] [picas_pwd]   #
# description: Set PiCaS environment for the communication with couchDB #
#              and start the pilot job                                  #
#                                                                       #
#          J.B.R. Oonk <oonk@strw.leidenuniv.nl>    -- Leiden/ASTRON    #
#          - dec 2015 updated this for FAD by JBRO                      #
#                                                                       #
# ===================================================================== #

set -x

globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/prefactor_sandbox_$1.tar file:`pwd`/sandbox_$1.tar
tar -xf sandbox_$1.tar

mv prefactor-sandbox/* . 
rm -rf prefactor-sandbox*.tar
rm -rf prefactor-sandbox/



chmod u+x prefactor.sh
ls -l

# Start the pilot jobs by contacting PiCaS tokens

python pilot.py $1 $2 $3 > pilot.log


