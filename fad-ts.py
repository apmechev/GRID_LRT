##########################
#Python script to check SURLS, stage files, create and run tokens
#
#Usage python fad.py srm_L229587.txt master_setup.cfg
# fad_v7- 	Add Y/N
#		Added check for proper input and srm filename
#version 1.0- 1-Feb2016
#
##########################

import glob
import tarfile
import os
import shutil
import sys
import re
import subprocess

if len(sys.argv)<3:
	print ""
	print "You need to input the SRM file and the master config file"
	print "ex.  python fad.py srm_L229587.txt master_setup.cfg"
	sys.exit()

if ("srm" in sys.argv[1]) and ("master_setup.cfg" in sys.argv[2]):
	srmfile=sys.argv[1]
	mastercfg=sys.argv[2]
elif ("srm" in sys.argv[2]) and ("master_setup.cfg" in sys.argv[1]):
        srmfile=sys.argv[2]
        mastercfg=sys.argv[1]
else: 
	print "there may be a typo in your filenames"
	sys.exit()

if srmfile== 'srm.txt': #If there's no obsid in the filename (ie pulled from LTA)
	with open(srmfile,'r') as f:
		line=f.readline()
		obs_name='L'+str(re.search("L(.+?)_",line).group(1))
		print "copying srm.txt into srm_L"+obs_name+".txt "
	shutil.copyfile('srm.txt','srm_'+obs_name+'.txt')
	srmfile='srm_'+obs_name+'.txt'

#re-extracts the FAD tarfile but only if not already there and sets up fadir
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


#Clean Tokens 
for stuff in glob.glob(fadir+'/Tokens/datasets/*'):
	shutil.rmtree(stuff)

#Clean Staging
for stuff in glob.glob(fadir+'/Staging/datasets/*'):
       shutil.rmtree(stuff)

for oldstagefile in glob.glob(fadir+"/Staging/*files*"):
     os.remove(oldstagefile)

#Maybe check if srm_L****.txt file in proper format?

obsid=srmfile.split("srm_")[1].split(".txt")[0]

os.makedirs(fadir+'/Tokens/datasets/'+obsid)
os.makedirs(fadir+'/Staging/datasets/'+obsid)
gsurl_v3.main(srmfile)

shutil.copy("srmlist",fadir+"/Tokens/datasets/"+obsid)
shutil.copy("subbandlist",fadir+"/Tokens/datasets/"+obsid)
shutil.copy("srmlist",fadir+"/Staging/datasets/"+obsid)
shutil.copy("subbandlist",fadir+"/Staging/datasets/"+obsid)



	#Adds OBSID to the master_setup.cfg and sends it to Staging and Tokens
for dir in ['Tokens','Staging']:
	with open(fadir+"/"+dir+"/datasets/"+obsid+"/setup.cfg","a") as cfgfile:
		cfgfile.write("[OBSERVATION]\n")
		cfgfile.write("OBSID           = "+obsid+"\n")
		with open('master_setup.cfg','r') as mastercfg:
			for i, line in enumerate(mastercfg):
				cfgfile.write(line)


	#append srms to the staging/files, reformat and add to files 
with open(fadir+"/Staging/"+obsid+"_files","a") as Stagefile:
	print("Pre-staging observation "+obsid)
	if "fz-juelich.de" in open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r').read():
		with open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r') as srms:
			for i,line in enumerate(srms):
				Stagefile.write(re.sub('srm:\/\/lofar-srm.fz-juelich.de:8443/','',line.split()[0])+'\n') #take first entry (srm://) ignoring file://
		Stagefile.close()
		fileloc='j'
	elif "srm.grid.sara.nl" in open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r').read():
		with open(fadir+"/Tokens/datasets/"+obsid+"/srmlist",'r') as srms:
			for i,line in enumerate(srms):
				Stagefile.write(re.sub('srm:\/\/srm.grid.sara.nl:8443','',line.split()[0])+'\n')
		Stagefile.close()
		fileloc='s'


print ""

os.chdir(fadir+"/Staging/")
for oldfile in glob.glob("files"):
       os.remove(oldfile)
sys.path.append(os.path.abspath("."))
shutil.copy(obsid+"_files","files")


#Maybe check if grid storage is online??
if fileloc=='s':
	import state
	locs=state.main('files')
	if len(locs)==0: 
		print "No files found!! State error"
		sys.exit()
	for sublist in locs:
		if 'NEARLINE' in sublist :
			os.system("python stage.py")
		
elif fileloc=='j':
	import state_fzj
	locs=state_fzj.main('files')
	for subs in locs:
		if 'NEARLINE' in subs :
        	        os.system("python stage_fzj.py")

print ""
os.chdir("../../")
os.chdir(fadir+"/Tokens/")
try:
    print "Your picas user is "+os.environ["PICAS_USR"]+" and you're in db "+os.environ["PICAS_DB"]
except KeyError:
    print " You haven't set $PICAS_DB!! \n\n Exiting"
    sys.exit()

subprocess.call(['python','removeObsIDTokens.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
subprocess.call(['python','createTokens.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
subprocess.call(['python','createViews.py',os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
subprocess.call(['python','createObsIDView.py',obsid,os.environ["PICAS_DB"],os.environ["PICAS_USR"],os.environ["PICAS_USR_PWD"]])
os.chdir("../../")

os.remove('srmlist')
os.remove('subbandlist')

##Wait for keystroke
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


if os.path.exists(fadir+"/Application/jobIDs"):
	os.remove(fadir+"/Application/jobIDs")

os.chdir(fadir+"/Application")
subprocess.call(['glite-wms-job-submit','-d',os.environ["USER"],'-o','jobIDs','avg_dmx.jdl'])
