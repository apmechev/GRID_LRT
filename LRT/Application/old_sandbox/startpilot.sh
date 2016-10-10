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

# Set permissions for the master script
chmod u+x master.sh

ls -l

# Start the pilot jobs by contacting PiCaS tokens

python pilot.py $1 $2 $3 > pilot.log

