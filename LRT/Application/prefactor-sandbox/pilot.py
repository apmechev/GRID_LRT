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
import sys,os
import time
import couchdb
import subprocess

#picas imports
from picas.actors import RunActor
from picas.clients import CouchClient
from picas.iterators import BasicViewIterator
from picas.modifiers import BasicTokenModifier
from picas.executers import execute

from update_token_status import update_status

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
        server = couchdb.Server(url="https://picas-lofar.grid.sara.nl:6984")
        server.resource.credentials = (str(sys.argv[2]),str(sys.argv[3]))
        db = server[str(sys.argv[1])]
	
        attachies=token["_attachments"].keys()
        for att in [s for s in attachies if "parset"  in s] : #TODO: Make only "parset" in attachy
            att_txt=db.get_attachment(token["_id"],att).read()
            with open(att,'w') as f:
                for line in att_txt:
                    f.write(line)
                if "parset" in att:
                    parsetfile=att
                else:
                    parsetfile="Pre-Facet-Cal.parset"

        for att in [s for s in attachies if "srm"  in s] : #TODO: Make only "parset" in attachy
            att_txt=db.get_attachment(token["_id"],att).read()
            print att
            print att_txt
            with open(att,'w') as f:
                for line in att_txt:
                    f.write(line)


        try:
            cal_obsid=" --calobsid "+str(token['CAL_OBSID'])+" "
        except:
            cal_obsid=""

        try:
            pipetype=" --pipetype "+str(token['pipeline'])+" "
        except:
            pipetype=""
        try:
                lofdir= str(token['lofar_sw_dir'])
        except:
                lofdir="/cvmfs/softdrive.nl/wjvriend/lofar_stack/2.16"
###calobsid:
	execute("ls -lat",shell=True)
        try:
            update_status(str(sys.argv[1]),str(sys.argv[2]),str(sys.argv[3]),token['_id'],'launched')
        except:
            pass
        

        if 'start_SB' in token.keys():
            start_SB=token['start_SB']
        elif 'start_AB' in token.keys():
            start_SB=token['start_AB']
        else:
            start_SB=""
	
        command = "/usr/bin/time -v ./master.sh --startsb " + str(start_SB) + " --numsb "+ str(token['num_per_node']) +" --parset "+ parsetfile+" --lofdir "+lofdir+" --obsid "+str(token['OBSID'])+pipetype+cal_obsid+" --token "+token["_id"] +" --picasdb "+ str(sys.argv[1]) +" --picasuname "+str(sys.argv[2])+" --picaspwd "+ str(sys.argv[3])+ " 2> logs_.err 1> logs_out"
        print command
        
	out = execute(command,shell=True)
        print 'exit status is ' 
        print out
#        token=self.client.modify_token(token)
        try:
            if out[0]==0:
                update_status(str(sys.argv[1]),str(sys.argv[2]),str(sys.argv[3]),token['_id'],'done')
                token['progress']=1.0
            else:
                update_status(str(sys.argv[1]),str(sys.argv[2]),str(sys.argv[3]),token['_id'],'error')
        except:
            pass
	# Get the job exit code in the token 
        token=db[token["_id"]]
        token['output']=out[0]
        
#	 token = self.modifier.close(token)
#	 self.client.db[token['_id']] = token ##Fix this update
        db.update([token])
        #token=self.client.modify_token(token)
        #self.modifier.add_output(token,out[0])
        token=db[token["_id"]]
        token = self.modifier.close(token)

        sols_search=subprocess.Popen(["find",".","-name","*.png"],stdout=subprocess.PIPE)
        result=sols_search.communicate()[0]

        for png in result.split():
            try:
                self.client.db.put_attachment(token,open(os.path.basename(png),'r'),os.path.split(png)[1])
            except:
                print "error attaching"+png
	# Attach logs in token

	
	curdate=time.strftime("%d/%m/%Y_%H:%M:%S_")
	try:
           logsout = "logs_out"
           log_handle = open(logsout, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logsout)
           logserr = "logs_.err"
           log_handle = open(logserr, 'rb')
           self.client.db.put_attachment(token,log_handle,curdate+logserr)
	except: 
  	   pass

def main():
    # setup connection to db
    db_name = sys.argv[1]
    client = CouchClient(url="https://picas-lofar.grid.sara.nl:6984", db=str(sys.argv[1]), username=str(sys.argv[2]), password=str(sys.argv[3]))
    # Create token modifier
    modifier = BasicTokenModifier()
    # Create iterator, point to the right todo view
    iterator = BasicViewIterator(client, sys.argv[4]+"/todo", modifier)
    # Create actor
    actor = ExampleActor(iterator, modifier)
    # Start work!
    print "Connected to the database %s sucessfully. Now starting work..." %(sys.argv[1])
    actor.run()

if __name__ == '__main__':
    main()
