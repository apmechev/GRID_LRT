import os
import sys
import glob
import shutil
import pyrap.tables as pt
import math


#--------------------------------------------------
# Versioning.
# - Original: JBR Oonk (ASTRON/LEIDEN) Sep 2015
# -  14/10/2015 (_v2): fixed some errors in _fa.parset definition  
# -  14/10/2015 (_v2): demixing gives an array non-conformance error (not fixed)
# -  12/02/2016 (_v2): added HBAdefault.rfis strategy file
# -
#--------------------------------------------------

# -------------------------------------------------
# TO RUN: python avg_dmx.py $path $avg_freq_step $avg_time_step $... > log_<obsID>_<subband> &

# additional requirements:
# - Ateam_LBA.sky.tar
#--------------------------------------------------


# parameters set by user when starting
# - note argv[0] 'lofar.obs.id' is only used for srm storing in .sh (not here in .py)
#
infile          = str(sys.argv[1])
avg_freq_step   = str(sys.argv[2])
avg_time_step   = str(sys.argv[3])
do_demix        = str(sys.argv[4])
demix_freq_step = str(sys.argv[5])
demix_time_step = str(sys.argv[6])
demix_sources   = str(sys.argv[7])
select_nl       = str(sys.argv[8])
parset		= str(sys.argv[9])

print 'infile: ', infile
print 'avgfrq: ', avg_freq_step
print 'avgtim: ', avg_time_step
print 'do dmx: ', do_demix
print 'dmxfrq: ', demix_freq_step
print 'dmxtim: ', demix_time_step
print 'dmxsrc: ', demix_sources
print 'sel nl: ', select_nl
print 'parset: ',parset

# example of expected input
#infile          = 'L400139_SB003_uv.dppp.MS'
#avg_freq_step   = 2
#avg_time_step   = 2
#do_demix        = False
#demix_freq_step = 2
#demix_time_step = 2
#demix_sources   = 'CasA' #comma separated if >1 i.e. CasA,CygA
#select_nl       = True



# START PROGRAM
print 'START AVG DMX:', infile


#SETUP 
#--------------------------------------------------
os.system('rm -rf Ateam_LBA.sky')
demix_sky = 'Ateam_LBA.sky.tar'
print 'Untarrring of:', demix_sky
os.system('tar -xvf ' + demix_sky)
#
dmxsky    = os.path.splitext(demix_sky)[0]
outfin    = infile+'.fa'
os.system('rm -rf ' + outfin)
#--------------------------------------------------
#Doing Time Splitting
#
#
#
#--------------------------------------------------
#
print '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+='
print 'Starting Chunking'
print '+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+='

import subprocess
import datetime
tmp=subprocess.Popen(['taql',"select TIME_RANGE  from "+infile+"/OBSERVATION"],stdout=subprocess.PIPE).communicate()[0].split()[-2:]
Start=tmp[0][1:].replace('-', '').replace(',','') #Proper Start/End formatting
End=tmp[1][:-1].replace('-', '')
print ("Start= ",Start," and End= ",End)
os.chdir(infile)
fsize=sum(os.path.getsize(f) for f in os.listdir('.') if os.path.isfile(f))
os.chdir("../")

ramsize=int(subprocess.Popen(['free'],stdout=subprocess.PIPE).communicate()[0].split()[9])#ram in kb
print("Chunking so that each chunk is less than 1/4 of "+str(ramsize)+" kb which is the RAM size as reported by free")
chsize=math.ceil(fsize/(ramsize*1000/2.))
if chsize<8000000000:
	print "\033[31m Chunks will be smaller than 8GB!! Aborting to avoid issues with AOFlag/Demix"
	sys.exit()
tms=[]
tme=[]
cnt=[]

if chsize<=1:
	cnt.append('_t001')
	tms.append(Start)
	tme.append(End)
else:
	cnt=[]
	tms.append(Start)
	st=datetime.datetime.strptime(Start, "%d%b%Y/%H:%M:%S.%f")
	en=datetime.datetime.strptime(End, "%d%b%Y/%H:%M:%S.%f")
	dur=(en-st).total_seconds()
	stride=int(dur/chsize)
	cnt.append('_t001')
	for i in range(int(chsize)):
		if i<chsize-1:
			tme.append((st+datetime.timedelta(0,stride*(i+1))).strftime("%d%b%Y/%H:%M:%S.%f")[:-3])
			tms.append((st+datetime.timedelta(0,stride*(i+1))).strftime("%d%b%Y/%H:%M:%S.%f")[:-3])
			cnt.append(str('_t'+str(format(i+2, '03'))))
	tme.append(End)

print 'Chunks created with start ',tms, ' and end times ',tme, ' and cnt= ', cnt

print "+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+="
print "Finished Chunking"
print "+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+=+="

#-------------------------------------------------
print 'Flag/Avg of:', infile

ndppp_fa_parset = infile + '_fa.parset' 
os.system('rm ' + ndppp_fa_parset)

obsid=infile.split("_")[0]
print "OBSID is "+ obsid

import infile_script
print "Processing parset:", ndppp_fa_parset

if not ".parset" in parset:
	shutil.copy("parsets/default.parset",ndppp_fa_parset)
	infile_script.msinmsout(ndppp_fa_parset,infile)
	infile_script.avgtimefreqstep(ndppp_fa_parset,avg_freq_step,avg_time_step)
	infile_script.dmxtimefreqstep(ndppp_fa_parset,demix_freq_step,demix_time_step)
	infile_script.dmxsources(ndppp_fa_parset,demix_sources)
	infile_script.dodmx(ndppp_fa_parset,do_demix)
	infile_script.selectnl(ndppp_fa_parset,select_nl)
else:
	shutil.copy("parsets/"+obsid+"_"+parset,ndppp_fa_parset)
	infile_script.msinmsout(ndppp_fa_parset,infile)

#--------------------------------------------------
# IF One Chunk, BYPASS!!
#
#-------------------------------------------------
#START LOOP TIME SPLIT

count=0
for (ts,te,ct) in zip(tms, tme, cnt):

  output=infile+ct

  print 'Flag/Avg of: ', output, ts, te, ct
  ndppp_fa_parset_ch=ndppp_fa_parset+"_chunk"+ct
  shutil.copy(ndppp_fa_parset,ndppp_fa_parset_ch)
  infile_script.msinmsout(ndppp_fa_parset_ch,infile,output)
  infile_script.timesteps(ndppp_fa_parset_ch,ts,te)

  os.system('NDPPP ' + ndppp_fa_parset_ch)
  #-------------------------------------------------
  #print 'Cleanup of:', infile
  #os.system('rm -rf ' + infile)
  #-------------------------------------------------

  print 'finished chunk: ', output, ts, te


#COLLECT ALL CHUNKS
cac=sorted(glob.glob('./*MS_t*'))
fls=cac
print 'Collect all time chunks: ', fls

#use pyrap tables for concat in time
t = pt.table(sorted(fls))
print 'Sorting the data on time'
t1= t.sort('TIME')
print 'Creating deep copy', outfin
t1.copy(outfin, deep = True)

#ndppp can not concat ms' in time
#cac=glob.glob('./*MS_t*')
#fls=''
#for nf in cac:
#    fls=fls+nf+','
#
#fls='['+fls[:-1]+']'
#print fls
#print 'Corrected file list: ', fls
#ndppp_cac_parset = infile + '_cac.parset' 
#os.system('rm ' + ndppp_cac_parset)
#fc=open(ndppp_cac_parset, 'w')
#fc.write('msin                    = %s\n' % fls)
#fc.write('msin.datacolumn         = DATA\n')
#fc.write('msin.autoweight         = false\n')
#fc.write('msout                   = %s\n' % outfin)
#fc.write('msout.datacolumn        = DATA\n')
#fc.write('steps                   = []\n')
#fc.close()
#os.system('NDPPP ' + ndppp_cac_parset)

print 'Finished deep copy: ', outfin


# Note output file has to be sent to GRID storage
print 'finished avg dmx of: ', outfin


