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
import sys
import time
import couchdb
import subprocess
import shutil
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
	location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox/sandbox_"+str(sys.argv[2])+"_"+str(token['OBSID'])+".tar"
	print location
	subprocess.call(["globus-url-copy", location, "sandbox.tar"])
	subprocess.call(["tar", "-xf", "sandbox.tar","-C",".","--strip-components=1"])
        subprocess.call(["chmod","u+x","prefactor.sh"])

	#This will process the token from the DOWNLOADED pilot.py (The timelines diverge at this point)
	from  pilot import ExampleActor as Actor2
	newactor= Actor2(self.iterator,self.modifier)
	newactor.process_token(key,token)
	return

 	   

def main():
    # setup connection to db
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
