#=========
#Updates the status of the token from a shell script or another python script
#
#=========

import couchdb
import os,sys,time

def update_freq(p_db,p_usr,p_pwd,tok_id,freq):
    try:
        server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (p_usr,p_pwd)
        db = server[p_db]
    except couchdb.http.ServerError:
        time.sleep(1)
        update_freq(p_db,p_usr,p_pwd,tok_id,freq)

    
    token=db[tok_id] 
    A_SBN=int(round((( ( float(freq)/1e6 - 100.0 ) / 100.0 ) * 512.0),0))
    if 'FREQ' in token.keys():
        token['FREQ']=freq
    token['ABN']=A_SBN
    db.update([token]) 
    print A_SBN

if __name__ == '__main__':
    update_freq(sys.argv[1],sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5])

