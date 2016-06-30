##########################
#Python script to check SURLS, stage files, create and run tokens
#
#Usage python fad.py srm_L229587.txt master_setup.cfg
# fad_v7- 	Add Y/N
#		Added check for proper input and srm filename
#		Added check for staging and if staging succeeded
#version 1.1-   17-Mar-2016
#version 1.2 -  3-Apr-2016
#		Now accepts a default parset with no master_setup
#		7-Apr-2016
#		Now accepts user defined parset in FAD_v#/parsets in custom_setup
#		Can Invoke scripts to modify parset on the node
#		--resubmit errors only implemented 
##########################

import glob
import tarfile
import os
import shutil
import sys
import re
import subprocess


###########
#Dictionary of input variables to make keeping track of values easier
###########

d_vars = {"srmfile":"","fadir":".","resuberr":False,"TSplit":True,"OBSID":"","sw_dir":"$VO_LOFAR_SW_DIR","sw_ver":"current","parsetfile":"-","jdl_file":"avg_dmx_prefactor.jdl","numpernode":10}


############
# Some checks on input arguments
############

def parse_arguments(args):
	if len(args)<3 or ("-h" in args[:-2] or ("--help" in args[:-2])):
		print ""
		print "You need to input the SRM file and the master config file"
		print "ex.  python fad-master.py [OPTIONS] srm_L229587.txt master_setup.cfg"
		print "optional flags ( -r, -j, -s, -noTS, -d, -v) come before srm and config file "
		print ""
		print "+=+=+=+= Current Options +=+=+=+="
		print "(-noTS or --no-time-splitting)	- turn off Time Splitting "
                print "(-r or --resub-error-only)   	- resubmit only error tokens "
                print "(-j or --jdl)		        - specify .jdl file to run  "
                print "(-d or --software-dir)           - path to custom LOFAR software dir "
                print "(-v or --software-version)       - software version (subfolder of software-dir)"
                print "(-n or --number-per-node)        - number of subbands per node (10 default)"
		print "(-h or --help)                   - prints this message (obv)"
		sys.exit()
	
	if ("srm" in args[-2]) and (".parset" in args[-1]):
		d_vars['srmfile']=sys.argv[-2]
		d_vars['parset']=sys.argv[-1]
	
	elif ("srm" in args[-1]) and (".parset" in args[-2]):
	        d_vars['srmfile']=args[-1]
		d_vars['parset']=args[-2]
	
	else: 
		print "there may be a typo in your filenames"
		sys.exit()
	
	d_vars['resuberr']=False
	d_vars['TSplit']=True

	if ("-r" in args[:-2] or ("--resub-error-only" in args[:-2])):
		print "\033[33mFlag set to resubmit only error tokens\033[0m"
		d_vars['resuberr']=True
	
	if ("-noTS" in args[:-2] or ("--no-time-splitting" in args[:-2])):
	        print "\033[33mTurning Off Timesplitting\033[0m"
	        d_vars['TSplit']=False
	if ("-d" in args[:-2] or ("--software-dir" in args[:-2])):
		try:
			idx=args.index("-d")
		except:
			idx=args.index("--software-dir")
		print "Using Software dir="+args[idx+1]
		d_vars['sw_dir']=args[idx+1]

	if ("-v" in args[:-2] or ("--software-version" in args[:-2])):
		try:
                        idxv=args.index("-v")
                except:
                        idxv=args.index("--software-version")
                print "Using Software version="+args[idxv+1]
                d_vars['sw_ver']=args[idxv+1]

        if ("-j" in args[:-2] or ("--jdl" in args[:-2])):
                try:
                        idxv=args.index("-j")
                except:
                        idxv=args.index("--jdl")
                print "Using jdl_file="+args[idxv+1]
                d_vars['jdl_file']=args[idxv+1]

        if ("-n" in args[:-2] or ("--number-per-node" in args[:-2])):
                try:
                        idxv=args.index("-n")
                except:
                        idxv=args.index("--number-per-node")
                print "Sending "+args[idxv+1]+" Subbands per node"
                d_vars['numpernode']=int(args[idxv+1])

	return()	
	
	
###########
#re-extracts the FAD tarfile if needed and sets up fad-dir
###########
def setup_dirs():

	print ""
	print "You're running \033[33m FAD1.0\033[0m Time-Splitting is \033[33m"+["OFF","ON"][d_vars['TSplit']]+"\033[0m"+[" By User Request"," By Default"][d_vars['TSplit']]+"!"
	print ""
	
	latest_tar=glob.glob('FAD_*[0-9]*.tar')[-1]
	if not latest_tar:
		d_vars['fadir']=glob.glob('FAD_*[0-9]*')[-1]
	if not os.path.isdir(os.path.splitext(latest_tar)[0]):
		print "Extracting "+ latest_tar
		tar=tarfile.open(latest_tar)
		tar.extractall()
		tar.close()
	
	if latest_tar:
		d_vars['fadir']=os.path.splitext(latest_tar)[0]

	with open(d_vars['srmfile'],'r') as f:
                line=f.readline()
                d_vars['OBSID']='L'+str(re.search("L(.+?)_",line).group(1))
                print "copying "+d_vars["OBSID"]+" srms into prefactor directory"

        with open(d_vars["srmfile"],'r') as f1:
                with open(d_vars["fadir"]+'/Application/prefactor-sandbox/prefactor/srm.txt', 'w') as f2:
                        lines = f1.readlines()
                        for i, line in enumerate(lines):
                                if d_vars["OBSID"] in line:
                                        f2.write(line)
	num_lines = sum(1 for line in open(d_vars["fadir"]+'/Application/prefactor-sandbox/prefactor/srm.txt'))
	print("Total number of subbands: "+str(num_lines)+" split into "+str(num_lines/d_vars["numpernode"]+[0,1][num_lines%d_vars["numpernode"]>0])+" tokens")

        #check if obsid exists in srm file\033[0m
        found=False
        with open(d_vars['srmfile'],'rt') as f:
                for line in f:
                        if d_vars['OBSID'] in line:
                                found=True
                                print("Processing OBSID=\033[32m"+d_vars['OBSID']+"\033[0m")
				break
                if not found:
                        print "\033[31mOBSID not found in SRM file!\033[0m"
                        sys.exit()

	
	sys.path.append(str(d_vars['fadir']+'/gsurl'))
	import gsurl_v3

	for stuff in glob.glob(d_vars['fadir']+'/Tokens/datasets/*'):
	        shutil.rmtree(stuff)
	
	for stuff in glob.glob(d_vars['fadir']+'/Staging/datasets/*'):
	       shutil.rmtree(stuff)
	
	for oldstagefile in glob.glob(d_vars['fadir']+"/Staging/*files*"):
	     os.remove(oldstagefile)
	
	
	os.makedirs(d_vars['fadir']+'/Tokens/datasets/'+d_vars['OBSID'])
	os.makedirs(d_vars['fadir']+'/Staging/datasets/'+d_vars['OBSID'])
	gsurl_v3.main(d_vars['srmfile'],stride=d_vars["numpernode"])  #creates srmlist and subbandlist files
	
	shutil.copy("srmlist",d_vars['fadir']+"/Tokens/datasets/"+d_vars['OBSID'])
	shutil.copy("subbandlist",d_vars['fadir']+"/Tokens/datasets/"+d_vars['OBSID'])
	os.remove("srmlist")
	os.remove("subbandlist")
	gsurl_v3.main(d_vars['srmfile'])  #creates srmlist and subbandlist files
	shutil.copy("srmlist",d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID'])
	shutil.copy("subbandlist",d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID'])
	
	for dir in ['Tokens','Staging']:
        	with open(d_vars['fadir']+"/"+dir+"/datasets/"+d_vars['OBSID']+"/setup.cfg","a") as cfgfile:
        	        cfgfile.write("[OBSERVATION]\n")
        	        cfgfile.write("OBSID           = "+d_vars['OBSID']+"\n")
        	        if len(d_vars['parsetfile'])<4:
        	                cfgfile.write('PARSET     = "-"\n')

	return 

####################
#Check state of files, if NEARLINE stage them
#If they're staged here, check if ONLINE_AND_NEARLINE and if not, abort
####################
def check_state_and_stage():

	with open(d_vars['fadir']+"/Staging/"+d_vars['OBSID']+"_files","a") as Stagefile:
	        print("Pre-staging observation "+d_vars['OBSID']+ " inside file " + Stagefile.name)
	        if "fz-juelich.de" in open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r').read():
	                with open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r') as srms:
	                        for i,line in enumerate(srms):
	                                line=re.sub("//pnfs","/pnfs",line)
	                                Stagefile.write(re.sub('srm:\/\/lofar-srm.fz-juelich.de:8443','',line.split()[0])+'\n') #take first entry (srm://) ignoring file://
	                Stagefile.close()
	                fileloc='j'
	        elif "srm.grid.sara.nl" in open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r').read():
	                with open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r') as srms:
	                        for i,line in enumerate(srms):
	                                line=re.sub("//pnfs","/pnfs",line)
	                                Stagefile.write(re.sub('srm:\/\/srm.grid.sara.nl:8443','',line.split()[0])+'\n')
	                Stagefile.close()
	                fileloc='s'
                elif "lofar.psnc.pl" in open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r').read():
                        with open(d_vars['fadir']+"/Staging/datasets/"+d_vars['OBSID']+"/srmlist",'r') as srms:
                                for i,line in enumerate(srms):
                                        line=re.sub("//pnfs","/pnfs",line)
                                        line=re.sub("//lofar","/lofar",line)
                                        Stagefile.write(re.sub('srm:\/\/lta-head.lofar.psnc.pl:8443','',line.split()[0])+'\n')
                        Stagefile.close()
                        fileloc='p'

	print "--"
	
	os.chdir(d_vars['fadir']+"/Staging/")
	
	for oldfile in glob.glob("files"):
	       os.remove(oldfile)
	sys.path.append(os.path.abspath("."))
	shutil.copy(d_vars['OBSID']+"_files","files")
	
	import state_all
	import stage_all
	locs=state_all.main('files')
	if len(locs)==0:
		print "No files found!! State error"
	for sublist in locs:
		if 'NEARLINE' in sublist :
			print "Nearline, add stage-all.py"	
                        stage_all.main('files')
                        print "Staging your file."
			
	locs=state_all.main('files')
	for sublist in locs:
               if 'NEARLINE' in sublist :
                               print "\033[31m+=+=+=+=+=+=+=+=+=+=+=+=+=+="
                               print "I've requested staging but srms are not ONLINE yet. I'll exit so the tokens don't crash. Re-run in a few (or tens of) minutes"
                               print "+=+=+=+=+=++=+=+=+=+=+=+=+=\033[0m"
                               sys.exit()
	print ""
	os.chdir("../../")
	#os.chdir(d_vars['fadir']+"/Tokens/")
	return 

####################
#PICAS Database Submission
#####################
def submit_to_picas():

        os.chdir(d_vars['fadir']+"/Tokens")
	try:
            print "Your picas user is "+os.environ["PICAS_USR"]+" and the DB is "+os.environ["PICAS_DB"]
        except KeyError:
            print "\033[31m You haven't set $PICAS_USR or $PICAS_DB or $PICAS_USR_PWD! \n\n Exiting\033[0m"
            sys.exit()

        if d_vars['resuberr']:
                subprocess.call(['python','resetErrorTokens.py',os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
        else:
                subprocess.call(['python','removeObsIDTokens.py',d_vars['OBSID'],os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
                subprocess.call(['python','createTokens.py',d_vars['OBSID'],os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
        subprocess.call(['python','createViews.py',os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
        subprocess.call(['python','createObsIDView.py',d_vars['OBSID'],os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
        os.chdir("../../")

        os.remove('srmlist')
        os.remove('subbandlist')

####################
#Submit job using glite-wms-job-submit
#As it turns out, in avg_dmx.jdl, the PICAS variables are not evaluated (new environment)
#to make this truly portable, (and safe), they are evaluated and replaced in the script
#and after the file is restored 
#####################

def start_jdl():

        if os.path.exists(d_vars['fadir']+"/Application/jobIDs"):
                os.remove(d_vars['fadir']+"/Application/jobIDs")

        os.chdir(d_vars['fadir']+"/Application")
        #TODO: Change avg_dmx's number of jobs to number of subbands
	if d_vars['jdl_file']=="": 
        	dmx_jdl=['avg_dmx_no-TS.jdl','avg_dmx.jdl'][d_vars['TSplit']] #If Tsplit=True (Default), file is avg_dmx.jdl else the other one
	else:
		dmx_jdl=d_vars['jdl_file']
        shutil.copy(dmx_jdl,'avg_dmx_with_variables.jdl')
        filedata=None
        with open(dmx_jdl,'r') as file:
            filedata = file.read()
        filedata = filedata.replace('$PICAS_DB $PICAS_USR $PICAS_USR_PWD', os.environ["PICAS_DB"]+" "+os.environ["PICAS_USR"]+" "+os.environ["PICAS_USR_PWD"])


        os.remove(dmx_jdl)

        num_lines = sum(1 for line in open('prefactor-sandbox/prefactor/srm.txt'))
        numprocess= num_lines/d_vars["numpernode"]+[0,1][num_lines%d_vars["numpernode"]>0]
        filedata=filedata.replace("Parameters=50","Parameters="+str(numprocess))
        with open(dmx_jdl,'w+') as file:
            file.write(filedata)


        subprocess.call(['glite-wms-job-submit','-d',os.environ["USER"],'-o','jobIDs',dmx_jdl])

        shutil.move('avg_dmx_with_variables.jdl',dmx_jdl)

##############
#Prepares the sandbox and zips and uploads to storage
#This will be pulled by the job on the node
#while a variable with the path will be passed to the token
##############
def prepare_sandbox():

	os.chdir(d_vars['fadir']+"/Application/prefactor-sandbox")
	try:
                os.remove("prefactor.tar")
        except OSError:
                pass
	
	if "$" in d_vars["sw_dir"]:
		testdir=os.environ[d_vars["sw_dir"][1:]]
	else:
		testdir=d_vars["sw_dir"]
	if os.path.isdir(testdir) and os.path.isdir(testdir+"/"+d_vars["sw_ver"]):
		pass
	else:
		print "directory "+testdir+"/"+d_vars["sw_ver"]+" doesn't exist Exiting"
		sys.exit()
	## move the appropriate .sh file to master.sh
 
	sub = subprocess.call(['sed','-i', 's/^SW_DIR=.*/SW_DIR='+d_vars["sw_dir"]+'/g', "prefactor.sh"])
        sub = subprocess.call(['sed','-i', 's/\/current\//\/'+d_vars["sw_ver"]+'\//g', "prefactor.sh"])	
	print("tarring everything")
	subprocess.call(["tar","-cf", "prefactor.tar","prefactor/"])	

	os.chdir("../")
	subprocess.call(["tar","-cf", "prefactor-sandbox.tar","prefactor-sandbox/"])
	resub = subprocess.call(['sed','-i', 's/\/'+d_vars["sw_ver"]+'\//\/current\//g', "prefactor-sandbox/prefactor.sh"]) #reverting
	sandbox_base_dir="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/sandbox"
        print "uploading sandbox to storage for pull by nodes"

	subprocess.call(["uberftp", "-rm",sandbox_base_dir+"/prefactor-sandbox_"+os.environ["PICAS_USR"]+".tar"])
	subprocess.call(['globus-url-copy', "file:"+os.environ["PWD"]+"/"+d_vars['fadir']+"/Application/prefactor-sandbox.tar",sandbox_base_dir+"/prefactor-sandbox_"+os.environ["PICAS_USR"]+".tar"])	

        os.chdir("../../")
	return


if __name__ == "__main__":
        parse_arguments(sys.argv)
	setup_dirs()
        prepare_sandbox()

        check_state_and_stage()
	
	####################
	##Wait for keystroke
	###################

	yes = set(['yes','y', 'ye','yea','yesh','Y','oui', ''])
	no = set(['no','n','N'])
	print ""
        print "Do you want to continue? Y/N (Enter continues)"

	from termios import tcflush, TCIOFLUSH
	tcflush(sys.stdin, TCIOFLUSH) #Flush input buffer to stop enter-spammers
	choice = raw_input().lower()

	if choice in yes:
	   pass
	elif choice in no:
	   sys.exit()
	else:
	   sys.exit()

	submit_to_picas()
	start_jdl()
	sys.exit()



###########
#Clean Directories and old parset
###########


devnl=open(os.devnull, 'w')
greproc=subprocess.Popen(['glite-wms-job-status','-i',"FAD_v1/Application/jobIDs"],stdout=subprocess.PIPE,stderr=devnl)
grep=greproc.communicate()[0]
greproc.wait()
if (grep.find("    Current Status:     Running")>1) or (grep.find("    Current Status:     Scheduled")>1):
	print grep
	print "\033[31mYour Job Is Still Running.\033[0m Please wait until it's set as 'Completed'. This should happen <15 mins after all tokens complete\nThis program will continue when all jobs are set to completed so that the correct parameters are sent to the node."
	sys.exit()

