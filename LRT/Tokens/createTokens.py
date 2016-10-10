# ===================================================================================== #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>	--  SURFsara			#
# helpdesk: Grid Services <grid.support@surfsara.nl>	--  SURFsara			#
#											#
# usage: python createTokens.py [obsID] [picas_db_name] [picas_username] [picas_pwd]	#
# description:										#
#	The 'datasets' folder in working directory contains the [obsID] input files	# 
#	Connect to PiCaS server with [picas_username] [picas_pwd]			#
#  	Load the tokens to [picas_db_name]:						#
#        	for each SB in the "datasets/[obsID]/subband" file			#
#            		create one token						#
# ===================================================================================== #

import sys
import os
import ConfigParser
if not 'couchdb' in sys.modules:
        import couchdb


def loadTokens(db,LRT_ver="1.5",tok_name="token"):
   OBSID = sys.argv[1]
   tokens = []

   #read each file in the "datasets/[OBSID]" directory
   subbandPath = 'datasets' + '/' + OBSID + '/' + 'subbandlist' #path to file with subbands
   srmPath     = 'datasets' + '/' + OBSID + '/' + 'srmlist' #path to file with SURL input
   setupfile   = 'datasets' + '/' + OBSID + '/' + 'setup.cfg' #path to file with conf. parameters

   #parse setup.cfg parameters
   config = ConfigParser.ConfigParser()
   config.read(setupfile)

   # for each subband create one token
   with open(subbandPath) as f1:
      for line in f1:
         subband_num = line.strip('\n')
         print subband_num         

         with open(srmPath) as f2:
	    for surl in f2:
   	       srminput = surl.strip('\n')
               if srminput.find('SB'+subband_num)!=-1:
                  SURL_SB = srminput
                  print subband_num, SURL_SB
	 try:
            lofdir=config.get('OBSERVATION','LOFARDIR')
         except:
            lofdir="/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16"
         token = {

            '_id': 'token_' + OBSID + '_' + str(subband_num)+"v"+LRT_ver,
            'type': tok_name,
	    'OBSID': config.get('OBSERVATION','OBSID'),
            'SURL_SUBBAND': SURL_SB,
            'AVG_FREQ_STEP': config.get('OBSERVATION','AVG_FREQ_STEP'),
            'AVG_TIME_STEP': config.get('OBSERVATION','AVG_TIME_STEP'),
            'DO_DEMIX': config.get('OBSERVATION','DO_DEMIX'),
            'DEMIX_FREQ_STEP': config.get('OBSERVATION','DEMIX_FREQ_STEP'),
            'DEMIX_TIME_STEP': config.get('OBSERVATION','DEMIX_TIME_STEP'),
            'DEMIX_SOURCES': config.get('OBSERVATION','DEMIX_SOURCES'),
            'SELECT_NL': config.get('OBSERVATION','SELECT_NL'),
            'PARSET':  config.get('OBSERVATION','PARSET'),
            'LOFARDIR': lofdir,
            'SUBBAND_NUM': subband_num,
            'lock': 0,
            'done': 0,
            'hostname': '',
            'scrub_count': 0,
            'output': ''
         }
         tokens.append(token)
   db.update(tokens)

def get_db(uname,pwd,dbn,srv="https://picas-lofar.grid.sara.nl:6984"):
    server = couchdb.Server(srv)
    server.resource.credentials = (username,pwd)
    db = server[dbn]
    return db

if __name__ == '__main__':
   #Create a connection to the server
   username = sys.argv[3]
   pwd = sys.argv[4]
   dbn= sys.argv[2]
   db = get_db(username,pwd,dbn)
   #Load the tokens to the databas
   loadTokens(db)
