import sys
if not 'couchdb' in sys.modules:
        import couchdb
from couchdb import Server
from couchdb.design import ViewDefinition

# python removeTokens.py [obsID] [db_name] [username] [pwd]
# - updated by JBR OONK (ASTRON/LEIDEN) DEC 2015
"""
   Connect to the server with [username] [pwd]
   Delete the documents in the [db_name] couchdb database:
"""

def deleteDocs(db):
     #v=db.view("Monitor/done")
     v=db.view("Observations/"+sys.argv[1])
     for x in v:
         document = db[x['key']]
         db.delete(document)

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
   #Delete the Docs in database
   deleteDocs(db)
