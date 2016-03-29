import os
import sys
import glob
import subprocess

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

print 'infile: ', infile
print 'avgfrq: ', avg_freq_step
print 'avgtim: ', avg_time_step
print 'do dmx: ', do_demix
print 'dmxfrq: ', demix_freq_step
print 'dmxtim: ', demix_time_step
print 'dmxsrc: ', demix_sources
print 'sel nl: ', select_nl
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
#os.system('rm -rf Ateam_LBA.sky')
subprocess.call(['rm','-rf','Ateam_LBA.sky'])
demix_sky = 'Ateam_LBA.sky.tar'
print 'Untarring of:', demix_sky
#os.system('tar -xvf ' + demix_sky)
subprocess.call(['tar','-xvf',demix_sky])
#
dmxsky    = os.path.splitext(demix_sky)[0]
calskymod = '3C380_MSSS.skymodel'
#outext='.ccfa'
insext='.inst'

output    = infile+'.fa'
outins     = infile+insext

#os.system('rm -rf ' + output)
subprocess.call(['rm','-rf',output])
#--------------------------------------------------


#-------------------------------------------------
print 'Flag/Avg of:', infile
ndppp_fa_parset = infile + '_fa.parset' 
#os.system('rm ' + ndppp_fa_parset)
subprocess.call(['rm',ndppp_fa_parset])
f=open(ndppp_fa_parset, 'w')
f.write('msin                    = %s\n' % infile)
f.write('msin.datacolumn         = DATA\n')
f.write('msin.autoweight         = false\n') #pre-proc data
#f.write('msin.autoweight         = true\n') #raw data
    
if select_nl == 'True' or select_nl == 'true' or select_nl == 'TRUE':
#if select_nl == 1:
   #f.write('msin.baseline           = CS*&;RS*&;CS*&RS*\n') #ALL-NL
   f.write('msin.baseline           = CS*&\n') #CS-ONLY

f.write('msout                   = %s\n' % output)
f.write('msout.datacolumn        = DATA\n')

if do_demix == 'False' or do_demix == 'false' or do_demix == 'FALSE':
#if do_demix == 0:
   f.write('steps                   = [flag,flagstat,flagamp,rficonsole,avg1]\n')
   f.write('avg1.type               = squash\n')
   f.write('avg1.freqstep           = %s\n' % avg_freq_step)
   f.write('avg1.timestep           = %s\n' % avg_time_step)
else:
   f.write('steps                   = [flag,flagstat,flagamp,rficonsole,demixer]\n')
   f.write('demixer.type            = demixer\n')
   f.write('demixer.corrtype        = cross\n')
   f.write('demixer.demixfreqstep   = %s\n' % demix_freq_step)
   f.write('demixer.demixtimestep   = %s\n' % demix_time_step)
   f.write('demixer.elevationcutoff = 0.0deg\n')
   f.write('demixer.ignoretarget    = F\n')
   f.write('demixer.modelsources    = []\n')

   f.write('demixer.subtractsources = [%s]\n' % demix_sources)

   f.write('demixer.ntimechunk      = 0\n')
   f.write('demixer.skymodel        = %s\n' % dmxsky)
   f.write('demixer.freqstep        = %s\n' % avg_freq_step)
   f.write('demixer.timestep        = %s\n' % avg_time_step)
   
f.write('rficonsole.type         = aoflagger\n')
#f.write('rficonsole2.type        = aoflagger\n')
f.write('rficonsole.strategy     = HBAdefault.rfis\n')
#f.write('rficonsole2.strategy    = HBAdefault.rfis\n')
f.write('rficonsole.memorymax    = 16\n') #mem in GB (1cpu=8Gb)
#f.write('rficonsole2.memorymax   = 16\n') #mem in GB (1cpu=8Gb)

f.write('flag.type               = preflagger\n')
f.write('flag.baseline           = [[CS001HBA0*,CS001HBA1*],[CS002HBA0*,CS002HBA1*],[CS003HBA0*,CS003HBA1*],[CS004HBA0*,CS004HBA1*],[CS005HBA0*,CS005HBA1*],[CS006HBA0*,CS006HBA1*],[CS007HBA0*,CS007HBA1*],[CS011HBA0*,CS011HBA1*],[CS013HBA0*,CS013HBA1*],[CS017HBA0*,CS017HBA1*],[CS021HBA0*,CS021HBA1*],[CS024HBA0*,CS024HBA1*],[CS026HBA0*,CS026HBA1*],[CS028HBA0*,CS028HBA1*],[CS030HBA0*,CS030HBA1*],[CS031HBA0*,CS031HBA1*],[CS032HBA0*,CS032HBA1*],[CS101HBA0*,CS101HBA1*],[CS103HBA0*,CS103HBA1*],[CS201HBA0*,CS201HBA1*],[CS301HBA0*,CS301HBA1*],[CS302HBA0*,CS302HBA1*],[CS401HBA0*,CS401HBA1*],[CS501HBA0*,CS501HBA1*]]\n')

f.write('flagamp.type            = preflagger\n')
f.write('flagamp.amplmin         = 1e-30\n')
f.write('flagstat.type           = preflagger\n')
f.write('flagstat.baseline       = [[RS210*],[CS013*]]\n')        

f.close()
subprocess.call(['cat',ndppp_fa_parset])
#os.system('NDPPP ' + ndppp_fa_parset)
subprocess.call(['NDPPP',ndppp_fa_parset])
#os.system('rm ' + ndppp_fa_parset)
#-------------------------------------------------


#--------------------------------------------------
print 'NDPPP predict gaincal of: ', output
#os.system('makesourcedb in='+calskymod+'  out=' +output+"/sky format='<'")
subprocess.call(['makesourcedb','in='+calskymod,'out='+output+'/sky','format=<'])

ndppp_precal_parset = output + '.pre.parset'
#os.system('rm ' + ndppp_precal_parset)
subprocess.call(['rm',ndppp_precal_parset])
f=open(ndppp_precal_parset, 'w')
f.write('msin                  = %s\n' % output)
f.write('msin.datacolumn       = DATA\n')
#f.write('msin.autoweight       = false\n') #pre-proc data
#f.write('msin.autoweight       = true\n') #raw data
#f.write('msin.baseline         = CS*&\n')
#f.write('msin.starttime        = 26Oct2013/22:00:00.0 \n') #test
#f.write('msin.endtime          = 26Oct2013/23:00:00.0 \n') #test
f.write('msout                 = %s\n' % output)
#f.write('msout.datacolumn      = DATA\n')
#f.write('msout.datacolumn      = CORRECTED_DATA\n')
f.write('steps                 = [gaincal]\n')
f.write('gaincal.caltype       = fulljones\n')
f.write('gaincal.sourcedb      = ' + output + '/sky\n')
f.write('gaincal.parmdb        = ' + output + '/instrument\n')
f.write('gaincal.maxiter       = 200\n')
f.write('gaincal.usebeammodel   = true\n') #KE
f.write('gaincal.usechannelfreq = false\n') #KE
#f.write('applycal.type	       = applycal\n')
#f.write('applycal.correction   = gain\n')
#f.write('applycal.parmdb       = ' + outavg +'/instrument\n')
f.close()
#os.system('NDPPP ' + ndppp_precal_parset)
subprocess.call(['NDPPP',ndppp_precal_parset])
#--------------------------------------------------


#--------------------------------------------------
print 'NDPPP apply gaincal of: ', output
ndppp_appcal_parset = output + '.app.parset'
#os.system('rm ' + ndppp_appcal_parset)
subprocess.call(['rm',ndppp_appcal_parset])
f=open(ndppp_appcal_parset, 'w')
f.write('msin                  = %s\n' % output)
f.write('msin.datacolumn       = DATA\n')
#f.write('msin.baseline         = CS*&\n')
#f.write('msin.starttime        = 26Oct2013/22:00:00.0 \n') #test
#f.write('msin.endtime          = 26Oct2013/23:00:00.0 \n') #test
f.write('msout                 = .\n')
f.write('msout.datacolumn      = CORRECTED_DATA\n')
f.write('steps                 = [applycal, applybeam]\n') #KE beam is "applied" when step=applybeam
#f.write('steps                 = [applycal]\n')
f.write('applycal.type         = applycal\n')
f.write('applycal.correction   = gain\n')
f.write('applycal.parmdb       = ' + output +'/instrument\n')
f.write('applybeam.usechannelfreq = false\n') #KE
f.close()
#os.system('NDPPP ' + ndppp_appcal_parset)
subprocess.call(['NDPPP',ndppp_appcal_parset])
#--------------------------------------------------


#--------------------------------------------------
#os.system('cp -r '+ output +'/instrument ' + outins +'\n')
subprocess.call(['cp','-r',output+'/instrument',outins])
#--------------------------------------------------


#--------------------------------------------------
#IMG-CONT-CS
iccext='.cicc'
outicc=output+iccext
print 'IMG-CS Selecting:', output
ndppp_fa_parset = outicc + '.parset' 
#os.system('rm ' + ndppp_fa_parset)
subprocess.call(['rm',ndppp_fa_parset])
f=open(ndppp_fa_parset, 'w')
f.write('msin                  = %s\n' % output)
#f.write('msin.datacolumn       = DATA\n')
f.write('msin.datacolumn       = CORRECTED_DATA\n')
f.write('msin.baseline         = CS*&\n')
f.write('msin.autoweight       = false\n')
f.write('msout                 = %s\n' % outicc)
f.write('msout.datacolumn      = DATA\n')
f.write('rficonsole.type       = aoflagger\n')
f.write('rficonsole.strategy   = HBAdefault.rfis\n')
f.write('rficonsole.memorymax  = 16\n') #mem in GB (1cpu=8Gb)
f.write('flguv.type            = uvwflagger\n')
f.write('flguv.uvmmin          = 20 \n')
f.write('flguv.uvmmax          = 80000 \n')
f.write('steps                 = [flguv,rficonsole]\n')
#f.write('steps                 = [rficonsole]\n')
#f.write('steps                 = []\n')
f.close()
#os.system('NDPPP ' + ndppp_fa_parset)
subprocess.call(['NDPPP',ndppp_fa_parset])
#os.system('rm ' + ndppp_fa_parset)

print 'CS-Imaging MS: ', outicc

# IMAGER SETTINGS
outfile   = outicc
outputim  = outicc + '.cimg'

#GOOD AWimager
#command = "awimager ms="+ outfile + " image=" + outputim + " weight=briggs robust=0 npix=512 cellsize=40arcsec data=DATA padding=1. niter=2000 stokes=I operation=mfclark wmax=20000 gain=0.1 timewindow=300 PBCut=0.01"
#print command
#os.system(command)
subprocess.call(['awimager','ms='+outfile,'image='+outputim,'weight=briggs','robust=0','npix=512','cellsize=40arcsec','data=DATA','padding=1.','niter=2000', 'stokes=I','operation=mfclark','wmax=20000','gain=0.1','timewindow=300','PBCut=0.01'])

print 'finished CS img of: ', output
#--------------------------------------------------


#-------------------------------------------------
#print 'Cleanup of:', infile
#os.system('rm -rf ' + infile)
#-------------------------------------------------


# Note output file has to be sent to GRID storage
print 'finished avg dmx of: ', output

