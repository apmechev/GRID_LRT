##########################
#Python script to send prefactor to GRID nodes 
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

############
# Some checks on input arguments
############

if len(sys.argv)<3:
	print ""
	print "You need to input the prefactor Parset and the srm list"
	print "ex.  python prefactor.py Pre-Facet-Cal.parset srm-files.txt -b bands-per-node (default 41)" 
	sys.exit()

if ("srm" in sys.argv[-2]) and (".parset" in sys.argv[-1]):
	srmfile=sys.argv[-2]
	prefactorparset=sys.argv[-1]

elif ("srm" in sys.argv[-1]) and (".parset" in sys.argv[-2]):
        srmfile=sys.argv[-1]
	prefactorparset=sys.argv[-2]

else: 
	print "there may be a typo in your filenames"
	sys.exit()

###########
#re-extracts the FAD tarfile if needed and sets up fadir
###########
print ""
print "You're running the GRID Prefactor Pipeline, dev version"  
print ""

latest_tar=glob.glob('FAD_*[0-9]*.tar')[-1]
if not latest_tar:
	fadir=glob.glob('FAD_*[0-9]*')[-1]
if not os.path.isdir(os.path.splitext(latest_tar)[0]):
	print "Extracting "+ latest_tar
	tar=tarfile.open(latest_tar)
	tar.extractall()
	tar.close()

if latest_tar:
	fadir=os.path.splitext(latest_tar)[0]
	
sys.path.append(str(fadir+'/gsurl'))
import gsurl_v3

###########
#Clean Directories and old parset
###########
for stuff in glob.glob(fadir+'/Tokens/datasets/*'):
	shutil.rmtree(stuff)

for stuff in glob.glob(fadir+'/Staging/datasets/*'):
       shutil.rmtree(stuff)

for oldstagefile in glob.glob(fadir+"/Staging/*files*"):
     os.remove(oldstagefile)

with open(srmfile, 'r') as f:
	 obsid=re.search('L[0-9]*',f.readline()).group(0)

#check if obsid exists in srm file
found=False
with open(srmfile,'rt') as f:
	for line in f:
		if obsid in line:
			found=True
			print obsid
	if not found:
		print "\033[31mOBSID not found in SRM file!\033[0m"
		sys.exit()
	


os.makedirs(fadir+'/Tokens/datasets/'+obsid)
os.makedirs(fadir+'/Staging/datasets/'+obsid)
gsurl_v3.main(srmfile)	#creates srmlist and subbandlist files

shutil.copy("srmlist",fadir+"/Tokens/datasets/"+obsid)
shutil.copy("subbandlist",fadir+"/Tokens/datasets/"+obsid)
shutil.copy("srmlist",fadir+"/Staging/datasets/"+obsid)
shutil.copy("subbandlist",fadir+"/Staging/datasets/"+obsid)



#Add tarring of parset files which will be untarred on the node

#subprocess.call(['cp','-r',fadir+"/parsets/*",fadir+"/Application/sandbox/scripts/parsets"])
os.chdir(fadir+"/Application/sandbox")
try:
	os.remove("scripts.tar")
except OSError:
	pass
subprocess.call(["tar","-cvf", "scripts.tar","scripts/"])
os.chdir("../../../")

devnl=open(os.devnull, 'w')
greproc=subprocess.Popen(['glite-wms-job-status','-i',"FAD_v1/Application/jobIDs"],stdout=subprocess.PIPE,stderr=devnl)
grep=greproc.communicate()[0]
greproc.wait()
if (grep.find("    Current Status:     Running")>1) or (grep.find("    Current Status:     Scheduled")>1):
	print grep
	print "\033[31mYour Job Is Still Running.\033[0m Please wait until it's set as 'Completed'. This should happen <15 mins after all tokens complete\nThis program will continue when all jobs are set to completed so that the correct parameters are sent to the node."
	sys.exit()



################
#Adds OBSID to the master_setup.cfg and sends it to Staging/ and Tokens/
################
for dir in ['Tokens','Staging']:
	with open(fadir+"/"+dir+"/datasets/"+obsid+"/setup.cfg","a") as cfgfile:
		cfgfile.write("[OBSERVATION]\n")
		cfgfile.write("OBSID           = "+obsid+"\n")

#################
#append srms to the staging/obsid_files, reformat and add to /Staging/files 
#################
with open(fadir+"/Staging/"+obsid+"_files","a") as Stagefile:
	print("Pre-staging observation "+obsid+ " inside file " + Stagefile.name)
	if "fz-juelich.de" in open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r').read():
		with open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r') as srms:
			for i,line in enumerate(srms):
				line=re.sub("//pnfs","/pnfs",line)
				Stagefile.write(re.sub('srm:\/\/lofar-srm.fz-juelich.de:8443','',line.split()[0])+'\n') #take first entry (srm://) ignoring file://
		Stagefile.close()
		fileloc='j'
	elif "srm.grid.sara.nl" in open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r').read():
		with open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r') as srms:
			for i,line in enumerate(srms):
                                line=re.sub("//pnfs","/pnfs",line)
				Stagefile.write(re.sub('srm:\/\/srm.grid.sara.nl:8443','',line.split()[0])+'\n')
		Stagefile.close()
		fileloc='s'
print "--"


####################
#Check state of files, if NEARLINE stage them
#If they're staged here, check if ONLINE_AND_NEARLINE and if not, abort
####################
os.chdir(fadir+"/Staging/")

for oldfile in glob.glob("files"):
       os.remove(oldfile)
sys.path.append(os.path.abspath("."))
shutil.copy(obsid+"_files","files")


#Maybe check if grid storage is online??

####################
#PICAS Database Submission
#####################
os.chdir("../Tokens/")

try:
    print "Your picas user is "+os.environ["PICAS_USR"]+" and the DB is "+os.environ["PICAS_DB"]
except KeyError:
    print "\033[31m You haven't set $PICAS_USR or $PICAS_DB or $PICAS_USR_PWD! \n\n Exiting\033[0m"
    sys.exit()
resuberr=False
if resuberr:
	subprocess.call(['python','resetErrorTokens.py',os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])     
else:
	subprocess.call(['python','removeObsIDTokens.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
	subprocess.call(['python','createTokens.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
subprocess.call(['python','createViews.py',os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
subprocess.call(['python','createObsIDView.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
os.chdir("../../")

os.remove('srmlist')
os.remove('subbandlist')


####################
##Wait for keystroke
###################
yes = set(['yes','y', 'ye', ''])
no = set(['no','n'])
print "Do you want to continue? Y/N (Enter continues)"
choice = raw_input().lower()

if choice in yes:
   pass
elif choice in no:
   sys.exit()
else:
   sys.exit()

####################
#Submit job using glite-wms-job-submit
#As it turns out, in avg_dmx.jdl, the PICAS variables are not evaluated (new environment)
#to make this truly portable, (and safe), they are evaluated and replaced in the script
#and after the file is restored 
#####################
if os.path.exists(fadir+"/Application/jobIDs"):
	os.remove(fadir+"/Application/jobIDs")

os.chdir(fadir+"/Application")
subprocess.call(["ls","-lat","sandbox/scripts/parsets"])
#TODO: Change avg_dmx's number of jobs to number of subbands

dmx_jdl='avg_dmx_prefactor.jdl'
shutil.copy(dmx_jdl,'avg_dmx_with_variables.jdl')
filedata=None
with open(dmx_jdl,'r') as file:
    filedata = file.read()
filedata = filedata.replace('$PICAS_DB $PICAS_USR $PICAS_USR_PWD', os.environ["PICAS_DB"]+" "+os.environ["PICAS_USR"]+" "+os.environ["PICAS_USR_PWD"])


os.remove(dmx_jdl)
with open(dmx_jdl,'w+') as file:
    file.write(filedata)


subprocess.call(['glite-wms-job-submit','-d',os.environ["USER"],'-o','jobIDs',dmx_jdl])

shutil.move('avg_dmx_with_variables.jdl',dmx_jdl)

