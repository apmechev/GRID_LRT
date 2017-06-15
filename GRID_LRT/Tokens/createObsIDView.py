# ============================================================================================= #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>	--  SURFsara				#
# helpdesk: Grid Services <grid.support@surfsara.nl>	--  SURFsara				#
#												#
# usage: python createObsIDView.py [obsID] [picas_db_name] [picas_username] [picas_pwd]		#
# description:											#
#	Connect to the server with [picas_username] [picas_pwd]					#
#	Create an [obsID] View (to include the corresponding obsID tokens) in [picas_db_name]:	#
#		obsid_view View : doc.obsID == [obsID]						#
# ============================================================================================= #

import sys
if not 'couchdb' in sys.modules:
	import couchdb
from couchdb import Server
from couchdb.design import ViewDefinition

def createViews(db,OBSID):
   OBSIDViewCode='''
      function(doc) {
         if(doc.type == "token") {
	    if (doc.OBSID == "%s"){
               emit(doc._id, doc._id);
	    }
         }
      }   
   '''
   # obsID View
   obsid_view = ViewDefinition('Observations', OBSID, OBSIDViewCode %(OBSID))
   obsid_view.sync(db)

def get_db():
    server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
    username = sys.argv[3]
    pwd = sys.argv[4]
    server.resource.credentials = (username,pwd)
    db = server[sys.argv[2]]
    return db

if __name__ == '__main__':
   #Create a connection to the server
   db = get_db()
   #Create the Views in database
   OBSID = sys.argv[1]
   createViews(db,OBSID)
