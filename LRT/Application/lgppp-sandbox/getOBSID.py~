# ===================================================================================== #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara            	#
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara            	#
#                                                                               	#
# usage: python pilot.py [picas_db_name] [picas_username] [picas_pwd]			#
# description:                                                                  	#
#	Connect to PiCaS server with [picas_username] [picas_pwd]               	#
#	Get the next token in todo View							#
#	Fetch the token parameters 							#
#	Run the main job (master_step23_v3.sh) with the proper input arguments		#
#	Get sterr and stdout in the output field of the token				#
# ===================================================================================== #

#python imports
import os
import sys
import time
import couchdb
import subprocess
import shutil
import glob

#picas imports
from picas.actors import RunActor
from picas.clients import CouchClient
from picas.iterators import BasicViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute

class ExampleActor(RunActor):
    def __init__(self, iterator, modifier):
        self.iterator = iterator
        self.modifier = modifier
        self.client = iterator.client

    def process_token(self, key, token):
	# Print token information
	location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/sandbox/sandbox_"+str(sys.argv[2])+"_"+".tar"
	print "Getting the sanbox from "+location
	subprocess.call(["globus-url-copy", location, "sandbox.tar"])
	print "Untarring Sandbox" 
	subprocess.call(["tar", "-xf", "sandbox.tar","-C",".","--strip-components=1"])
        os.system('ls *')
	for exefile in glob.glob("*.sh"):
		subprocess.call(["chmod","u+x",exefile])
	
	print "Running the pilot that came with the sandbox!"
	from  pilot import ExampleActor as Actor2
	newactor= Actor2(self.iterator,self.modifier)
	newactor.process_token(key,token)
	return

 	   

def main():
    # setup connection to db
    print "starting getOBSID"
    db_name = sys.argv[1]
    client = CouchClient(url="https://picas-lofar.grid.sara.nl:6984", db=str(sys.argv[1]), username=str(sys.argv[2]), password=str(sys.argv[3]))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create iterator, point to the right todo view
    iterator = BasicViewIterator(client, "Monitor/todo", modifier)
    # Create actor
    actor = ExampleActor(iterator, modifier)
    # Start work!
    actor.run()

if __name__ == '__main__':
    main()
