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
#sys.exit()

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
if not ".parset" in parset:
	shutil.copy("parsets/default.parset",ndppp_fa_parset)
else:
	shutil.copy("parsets/"+obsid+"_"+parset,ndppp_fa_parset)

print "Processing parset:", ndppp_fa_parset

import infile_script
infile_script.main(ndppp_fa_parset,infile)

#f=open(ndppp_fa_parset, 'w')
#f.write('msin                    = %s\n' % infile)
#f.write('msin.datacolumn         = DATA\n')
#f.write('msin.autoweight         = false\n')
#
#if select_nl == 'True' or select_nl == 'true' or select_nl == 'TRUE':
##if select_nl == 1:
#   f.write('msin.baseline           = CS*&;RS*&;CS*&RS*\n')
#
#f.write('msout                   = %s\n' % output)
#f.write('msout.datacolumn        = DATA\n')
#
#if do_demix == 'False' or do_demix == 'false' or do_demix == 'FALSE':
##if do_demix == 0:
##   f.write('steps                   = [rficonsole,flag,flagamp,avg1,rficonsole2]\n')
#   f.write('steps                   = [flag,flagamp,avg1]\n')
#   f.write('avg1.type               = squash\n')
#   f.write('avg1.freqstep           = %s\n' % avg_freq_step)
#   f.write('avg1.timestep           = %s\n' % avg_time_step)
#else:
#   f.write('steps                   = [flag,flagamp,demixer]\n')
#   f.write('demixer.type            = demixer\n')
#   f.write('demixer.corrtype        = cross\n')
#   f.write('demixer.demixfreqstep   = %s\n' % demix_freq_step)
#   f.write('demixer.demixtimestep   = %s\n' % demix_time_step)
#   f.write('demixer.elevationcutoff = 0.0deg\n')
#   f.write('demixer.ignoretarget    = F\n')
#   f.write('demixer.modelsources    = []\n')
#
#   f.write('demixer.subtractsources = [%s]\n' % demix_sources)
#
#   f.write('demixer.ntimechunk      = 0\n')
#   f.write('demixer.skymodel        = %s\n' % dmxsky)
#   f.write('demixer.freqstep        = %s\n' % avg_freq_step)
#   f.write('demixer.timestep        = %s\n' % avg_time_step)
#   
#f.write('rficonsole.type         = aoflagger\n')
#f.write('rficonsole2.type        = aoflagger\n')
#f.write('rficonsole.strategy     = HBAdefault.rfis\n')
#f.write('rficonsole2.strategy    = HBAdefault.rfis\n')
#f.write('rficonsole2.memorymax   = 3\n')
#f.write('rficonsole1.memorymax   = 3\n')
#
#f.write('flag.type               = preflagger\n')
#f.write('flag.baseline           = [[CS001HBA0*,CS001HBA1*],[CS002HBA0*,CS002HBA1*],[CS003HBA0*,CS003HBA1*],[CS004HBA0*,CS004HBA1*],[CS005HBA0*,CS005HBA1*],[CS006HBA0*,CS006HBA1*],[CS007HBA0*,CS007HBA1*],[CS011HBA0*,CS011HBA1*],[CS013HBA0*,CS013HBA1*],[CS017HBA0*,CS017HBA1*],[CS021HBA0*,CS021HBA1*],[CS024HBA0*,CS024HBA1*],[CS026HBA0*,CS026HBA1*],[CS028HBA0*,CS028HBA1*],[CS030HBA0*,CS030HBA1*],[CS031HBA0*,CS031HBA1*],[CS032HBA0*,CS032HBA1*],[CS101HBA0*,CS101HBA1*],[CS103HBA0*,CS103HBA1*],[CS201HBA0*,CS201HBA1*],[CS301HBA0*,CS301HBA1*],[CS302HBA0*,CS302HBA1*],[CS401HBA0*,CS401HBA1*],[CS501HBA0*,CS501HBA1*]]\n')
#
#f.write('flagamp.type            = preflagger\n')
#f.write('flagamp.amplmin         = 1e-30\n')
#
#f.close()
os.system('NDPPP ' + ndppp_fa_parset)
#os.system('rm ' + ndppp_fa_parset)
#-------------------------------------------------


#-------------------------------------------------
#print 'Cleanup of:', infile
#os.system('rm -rf ' + infile)
#-------------------------------------------------


# Note output file has to be sent to GRID storage
print 'finished avg dmx of: ', output

