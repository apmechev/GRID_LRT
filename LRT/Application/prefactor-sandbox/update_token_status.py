#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time

def update_status(p_db,p_usr,p_pwd,tok_id,status):
    try:
        server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (p_usr,p_pwd)
        db = server[p_db]
    except couchdb.http.ServerError:
        time.sleep(1)
        update_status(p_db,p_usr,p_pwd,tok_id,status)

    token=db[tok_id] 
    token['status']=status
    token['times'][status]=time.time()
    if status=='done':
        try:
            token['progress']=1
        except KeyError:
            pass
    db.update([token]) 
    with open('pipeline_status','w') as stat_file:
        stat_file.write(status)

if __name__ == '__main__':
    update_status(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

