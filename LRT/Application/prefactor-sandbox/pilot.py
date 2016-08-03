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
        print "-----------------------"
        print "Working on token: " + token['_id']
        for k, v in token.iteritems():
            print k, v
        print "-----------------------"

        # Start running the main job
        #
        # !!!! should try to get SB number from SURL to get unique OBSID+SB combination for logs (to replace SURL_SUBBAND here) TBD !!!!
        #
	
#        command = "valgrind --tool=memcheck --track-fds=yes --trace-children=yes --log-file=CACHEgrind%p  ./master_avg_dmx_v2.sh "+ str(token['OBSID']) + " " + str(token['SURL_SUBBAND']) + " " + str(token['AVG_FREQ_STEP']) + " " + str(token['AVG_TIME_STEP']) + " " + str(token['DO_DEMIX']) + " " + str(token['DEMIX_FREQ_STEP']) + " " + str(token['DEMIX_TIME_STEP']) + " " + str(token['DEMIX_SOURCES']) + " " + str(token['SELECT_NL']) + " " + str(token['SUBBAND_NUM']) + " 2> logs_" + str(token['OBSID']) + "_" + str(token['SUBBAND_NUM']) + ".err 1> logs_" + str(token['OBSID']) + "_" + str(token['SUBBAND_NUM']) + ".out" ##CACHEGRIND VERSION
	try:
		parsetfile= "prefactor/"+str(token['PARSET'])
	except:
		parsetfile="prefactor/Pre-Facet-Cal.parset"
        try:
                lofdir= str(token['LOFARDIR'])
        except:
                lofdir="/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16"
	
	execute("ls -lat",shell=True)
	command = "/usr/bin/time -v ./prefactor.sh " + str(token['SUBBAND_NUM']) + " "+ str(token['AVG_FREQ_STEP']) +" "+ parsetfile+" "+lofdir+" 2> logs_.err 1> logs_out"
        print command
        
	out = execute(command,shell=True)

	# Get the job exit code in the token 
        token['output'] = out[0]

	token = self.modifier.close(token)
	self.client.db[token['_id']] = token

	# Attach logs in token
	#self.client.db.put_attachment(token,out[1],filename="stdout")
	#self.client.db.put_attachment(token,out[2],filename="stderr")
	curdate=time.strftime("%d/%m/%Y_%H:%M:%S_")
	try:
           logsout = "logs_out"
           log_handle = open(logsout, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logsout)
           logserr = "logs_.err"
           log_handle = open(logserr, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logserr)
	   logs_zipped_pngs="pngs.tar.gz"
	   log_handle = open(logs_zipped_pngs, 'rb')
	   self.client.db.put_attachment(token,log_handle,curdate+log_zipped_pngs)
           #logcal = "logcal_" + str(token['OBSID']) + "_" + str(token['subband_cal']) + "_uv.MS"
           #log_handle = open(logcal, 'rb')
           #self.client.db.put_attachment(token,log_handle,curdate+logcal+".log")
	   #logsrc = "logsrc_" + str(token['obsID']) + "_" + str(token['subband_src']) + "_uv.MS"
           #log_handle = open(logsrc, 'rb')
	   #self.client.db.put_attachment(token,log_handle,curdate+logsrc+".log")
           #logtar = "logtar_" + str(token['obsID']) + "_" + str(token['subband_src']) + "_uv.MS.fs.msc"
           #log_handle = open(logtar, 'rb')
           #self.client.db.put_attachment(token,log_handle,curdate+logtar+".log")
	except: 
  	   pass

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
    print "Connected to the database %s sucessfully. Now starting work..." %(sys.argv[1])
    actor.run()

if __name__ == '__main__':
    main()
