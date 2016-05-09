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

############
# Some checks on input arguments
############

if len(sys.argv)<3:
	print ""
	print "You need to input the SRM file and the master config file"
	print "ex.  python fad-master.py srm_L229587.txt master_setup.cfg"
	print "optional flags ( -r or --resub-error-only) come after fad-master.py "
	sys.exit()

if ("srm" in sys.argv[-2]) and (".cfg" in sys.argv[-1]):
	srmfile=sys.argv[-2]
	mastercfg=sys.argv[-1]

elif ("srm" in sys.argv[-1]) and (".cfg" in sys.argv[-2]):
        srmfile=sys.argv[-1]
	mastercfg=sys.argv[-2]

else: 
	print "there may be a typo in your filenames"
	sys.exit()
resuberr=False

if ("-r" in sys.argv[:-2] or ("--resub-error-only" in sys.argv[:-2])):
	print "\033[33mFlag set to resubmit only error tokens\033[0m"
	resuberr=True


if srmfile== 'srm.txt': #If filename is just srm.txt TODO: Maybe catch other filenames
	with open(srmfile,'r') as f:
		line=f.readline()
		obs_name='L'+str(re.search("L(.+?)_",line).group(1))
		print "copying srm.txt into srm_L"+obs_name+".txt "
	shutil.copyfile('srm.txt','srm_'+obs_name+'.txt')
	srmfile='srm_'+obs_name+'.txt'
parsetfile=""
with open(mastercfg,'r') as readparset:
	for line in readparset:
		if "PARSET" in line:
			parsetfile=line.split("PARSET",1)[1].split("= ")[1].split('\n')[0]



###########
#re-extracts the FAD tarfile if needed and sets up fadir
###########
print ""
print "You're running the \033[33m FAD1.0 \033[0m Time-Splitting is \033[33mON\033[0m by Default!"
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

for oldparset in glob.glob(fadir+"/Application/sandbox/scripts/parsets/*.parset"):
	if (not parsetfile=="") and (not "default" in  oldparset ): ##Remove old parsets but not the default.parset
		os.remove(oldparset)
	#TODO Maybe check if srm_L****.txt file in proper format?

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

if not ((len(parsetfile)<4) or ("fault" in parsetfile) or parsetfile=="DEFAULT"):	
	shutil.copy(fadir+"/parsets/"+parsetfile,fadir+"/Application/sandbox/scripts/parsets/")

	

#Add tarring of parset files which will be untarred on the node

#subprocess.call(['cp','-r',fadir+"/parsets/*",fadir+"/Application/sandbox/scripts/parsets"])
os.chdir(fadir+"/Application/sandbox")
try:
	os.remove("scripts.tar")
except OSError:
	pass
subprocess.call(["tar","-cvf", "scripts.tar","scripts/"])
os.chdir("../../../")







################
#Adds OBSID to the master_setup.cfg and sends it to Staging/ and Tokens/
################
for dir in ['Tokens','Staging']:
	with open(fadir+"/"+dir+"/datasets/"+obsid+"/setup.cfg","a") as cfgfile:
		cfgfile.write("[OBSERVATION]\n")
		cfgfile.write("OBSID           = "+obsid+"\n")
		with open(mastercfg,'r') as cfg:
			for i, line in enumerate(cfg): 
				if 'PARSET' in line and len(parsetfile)<4:# if a parset is not defined
					continue  #don't write PARSET= "", will be handled below
				cfgfile.write(line)
		if len(parsetfile)<4:
			cfgfile.write('PARSET     = "-"\n')


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
if fileloc=='s':
	import state
	locs=state.main('files')
	if len(locs)==0: 
		print "No files found!! State error"
		sys.exit()
	for sublist in locs:
		if 'NEARLINE' in sublist :
			os.system("python stage.py")
			print "Staging your file."
	##TODO Would be nice not to check this twice if staged
	locs=state.main('files')
	for sublist in locs:
		if 'NEARLINE' in sublist :
			print "\033[31m+=+=+=+=+=+=+=+=+=+=+=+=+=+="
			print "I've staged the file but it's not ONLINE yet. I'll exit so bad things don't happen"
			print "+=+=+=+=+=++=+=+=+=+=+=+=+=\033[0m" 
			sys.exit()
		
elif fileloc=='j':
	import state_fzj
	locs=state_fzj.main('files')
	for subs in locs:
		if 'NEARLINE' in subs :
        	        os.system("python stage_fzj.py")
                        print "Staging your file"

	locs=state_fzj.main('files')
	for subs in locs:
		if 'NEARLINE' in subs :
			print "\033[31m+=+=+=+=+=+=+=+=+=+=+=+=+=+="
                        print "I've staged the file but it's not ONLINE yet. I'll exit so bad things don't happen"
                        print "+=+=+=+=+=+=+=+=+=+=+=+=+=+=\033[0m"
			sys.exit()


print ""
os.chdir("../../")
os.chdir(fadir+"/Tokens/")


####################
#PICAS Database Submission
#####################
try:
    print "Your picas user is "+os.environ["PICAS_USR"]+" and the DB is "+os.environ["PICAS_DB"]
except KeyError:
    print "\033[31m You haven't set $PICAS_USR or $PICAS_DB or $PICAS_USR_PWD! \n\n Exiting\033[0m"
    sys.exit()

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

shutil.copyfile('avg_dmx.jdl','avg_dmx_with_variables.jdl')
filedata=None
with open('avg_dmx.jdl','r') as file:
    filedata = file.read()
filedata = filedata.replace('$PICAS_DB $PICAS_USR $PICAS_USR_PWD', os.environ["PICAS_DB"]+" "+os.environ["PICAS_USR"]+" "+os.environ["PICAS_USR_PWD"])
with open('avg_dmx.jdl','w') as file:
    file.write(filedata)


subprocess.call(['glite-wms-job-submit','-d',os.environ["USER"],'-o','jobIDs','avg_dmx.jdl'])

shutil.move('avg_dmx_with_variables.jdl','avg_dmx.jdl')

