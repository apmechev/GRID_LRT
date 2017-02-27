import sys
if not 'couchdb' in sys.modules:
        import couchdb
from couchdb import Server
from couchdb.design import ViewDefinition
import pdb

# python removeTokens.py [db_name] [username] [pwd]
"""
   Connect to the server with [username] [pwd]
   Delete the documents in the [db_name] couchdb database:
"""

def deleteDocs(db):
     v=db.view("Monitor/error") 
     for x in v:
         pdb.set_trace()
         document = db[x['key']]
         db.delete(document)

def get_db():
    server = couchdb.Server("https://picas-lofar.grid.sara.nl:6984")
    username = sys.argv[2]
    pwd = sys.argv[3]
    server.resource.credentials = (username,pwd)
    db = server[sys.argv[1]]
    return db

if __name__ == '__main__':
   #Create a connection to the server
   db = get_db()
   #Delete the Docs in database
   deleteDocs(db)
