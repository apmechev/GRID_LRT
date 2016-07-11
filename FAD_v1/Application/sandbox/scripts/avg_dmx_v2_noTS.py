import os
import sys
import glob
import shutil

#--------------------------------------------------
# Versioning.
# - Original: JBR Oonk (ASTRON/LEIDEN) Sep 2015
# -  14/10/2015 (_v2): fixed some errors in _fa.parset definition  
# -  14/10/2015 (_v2): demixing gives an array non-conformance error (not fixed)
# -  12/02/2016 (_v2): added HBAdefault.rfis strategy file
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
print 'Untarring of:', demix_sky
os.system('tar -xvf ' + demix_sky)
#
dmxsky    = os.path.splitext(demix_sky)[0]
output    = infile+'.fa'
os.system('rm -rf ' + output)
#--------------------------------------------------


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
	shutil.copy("parsets/"+parset,ndppp_fa_parset)
	infile_script.msinmsout(ndppp_fa_parset,infile)



os.system('NDPPP ' + ndppp_fa_parset)
#os.system('rm ' + ndppp_fa_parset)
#-------------------------------------------------


#-------------------------------------------------
#print 'Cleanup of:', infile
#os.system('rm -rf ' + infile)
#-------------------------------------------------


# Note output file has to be sent to GRID storage
print 'finished avg dmx of: ', output

