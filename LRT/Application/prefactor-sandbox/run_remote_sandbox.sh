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
#Remove the tarfiles and just pull GRID picastools from git

#git clone https://github.com/apmechev/GRID_picastools.git .

#ls /cvmfs/softdrive.nl/apmechev/lofar_prof/2_18/

/usr/bin/python getOBSID.py $1 $2 $3 $4
export p_un=${2}
export p_pw=${3}
export p_db=${1}

echo "Pulling down the sandbox for OBSID "$OBSID" from /pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox/sandbox_$2_$OBSID.tar with token type $4"






ls -l
cat log*
# Start the pilot jobs by contacting PiCaS tokens



