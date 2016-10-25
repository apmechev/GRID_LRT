#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time,pdb

def update_status(p_db,p_usr,p_pwd):
    server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
    server.resource.credentials = (p_usr,p_pwd)
    db = server[p_db]
    statuses=[]
    

    while True:
        statuses=[]
        try:
            for i in db:
                try:
                    statuses.append(db[i]['status'])
                except KeyError:
                    pass  
            if len(filter(lambda x: x=='downloading',statuses))<5:
                sys.exit()
            else:
                time.sleep(1)
        except couchdb.http.ServerError:
            print "couchDB threw ServerError"
            time.sleep(30)

if __name__ == '__main__':
    update_status(sys.argv[1],sys.argv[2],sys.argv[3])

