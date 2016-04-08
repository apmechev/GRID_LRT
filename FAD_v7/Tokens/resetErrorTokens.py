# ============================================================================= #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>	--  SURFsara		#
# helpdesk: Grid Services <grid.support@surfsara.nl>	--  SURFsara		#
#										#
# usage: python resetTokens.py [picas_db_name] [picas_username] [picas_pwd]	#
# description:									#
#	Connect to PiCaS server with [picas_username] [picas_pwd]		#
#	Reset all the Error Tokens and add them in todo View			#
#	Update the database							#
# ============================================================================= #

#python imports
import sys
import time
if not 'couchdb' in sys.modules: 
	import couchdb

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

    def reset(self):
        server = self.client.server
        db = self.client.db
        v = db.view("Monitor/error")
        to_update = []
        for x in v:
            document = db[x['key']]
            document['lock'] = 0
	    document['done'] = 0
            document['scrub_count'] += 1
            document['hostname'] = ''
	    document['output'] = ''
            to_update.append(document)
        db.update(to_update)

def reset():
    client = CouchClient(url="https://picas-lofar.grid.sara.nl:6984", db=str(sys.argv[1]), username=str(sys.argv[2]), password=str(sys.argv[3]))
    modifier = BasicTokenModifier()
    iterator = BasicViewIterator(client, "Monitor/todo", modifier)
    actor = ExampleActor(iterator, modifier)
    return actor.reset()

if __name__ == '__main__':
    reset()
