#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time

def update_status(p_db,p_usr,p_pwd,tok_id,status):
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    token=db[tok_id] 
    token['status']=status
    token['times'][status]=time.time()
    db.update([token]) 
    with open('pipeline_status','w') as stat_file:
        stat_file.write(status)

if __name__ == '__main__':
    update_status(os.environ['p_db'],os.environ['p_un'],os.environ['p_pw'],sys.argv[1],sys.argv[2])

