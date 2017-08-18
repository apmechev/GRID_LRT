#! /bin/bash

# DIRECTORIES, Note no "/" at the end
# Data working directory
#WORK_DIR=/net/para13/data2/psalas/DDT001/CygA
# log directory
mkdir -p  ${PWD}/logs
export LOGS_DIR=${PWD}/logs
#cd ${WORK_DIR}

## bash stop on error ##
#set -e
## bash output things helpful for debugging ##
set -x

# source the lofar software

# Specify number of cores
NCORES=8
export OMP_NUM_THREADS=${NCORES}
# Memory
MMAX=15
################################## USER DEFINED ####################################
ts=sb028
# `printf "%1d" ${PBS_ARRAYID}`
export START_SB=${STARTSB}
echo $START_SB $OBSID
MS=${OBSID}_SB${START_SB}_uv.MS
LOGID=gaincal
BADANTPARSET=ndppp.badant.sb028.parset # badantflag
ATEAM=Ateam_LBA.sky # For demixing
FLAGPARSET=ndppp.usrflags.parset # usrflag
MODEL=cyga_john.skymodel # calibrate
CALTYPE=fulljones
SOURCES= #CasA
PARMDB=cyga_john_sb${START_SB}_wbeam.parmdb # correct
NITER=10000
MAXUV=12000
THRESHOLD=0.1
ROBUST=-1.5
wsclean=/cvmfs/softdrive.nl/lofar_sw/wsclean/wsclean-2.3/build/wsclean
NEWMOD=casa_cc16.skymodel
# Steps
filter=false
iniflag=true
badantflag=false
rfiflag=false
demix=false
rfiflag2=false
average_time=false
average_freq=false
rfiflag3=false
usrflag=false
calibrate=false
correct=false
rfiflag4=false
cleanimag=false
makemodel=false
subtract=false
################################## FILTER RS    ####################################
MSOUT=$(printf '%s\n' "${MS%.MS}_CS.MS")

if [ ${filter} = 'true' ];
then

PARSET=filter.t${ts}.parset
cat > ${PARSET} << EOF
msin              = ${MS}
msin.autoweight   = FALSE
msin.datacolumn   = DATA
msout             = ${MSOUT}
msout.datacolumn  = DATA
steps             = [filter]
filter.type       = filter
filter.baseline   = CS* &
filter.remove     = true
EOF
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'filter'

cat ${PARSET}

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.filter.t${ts}.log 2>&1
rm ${PARSET}

fi

if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## INITIALFLAGS ####################################
MSOUT=$(printf '%s\n' "${MS%.MS}_iflag.MS")
if [ "$iniflag" = true ];
then

PARSET=iniflag.t${ts}.parset
cat > ${PARSET} << EOF
msin               = ${MS}
msin.datacolumn        = DATA
msout                  = ${MSOUT} 
msout.datacolumn       = DATA
msout.writefullresflag = False
steps                  = [avg,flagamp]
avg.type               = average
avg.freqstep           = 4
flagamp.type           = preflagger
flagamp.amplmin = 1e-30
EOF

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'initflag'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.iniflag.t${ts}.log 2>&1
rm ${PARSET}

fi

if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## USER FLAGS  ####################################
if [ "$badantflag" = true ];
then

#if [ -f ${BADANTPARSET} ];
#then

PARSET=badant.parset
cat > ${PARSET} << EOF
msin               = ${MS}
msin.datacolumn    = DATA
msout              =
steps              = [badant1, badtime1]
badant1.type       = preflagger
badant1.baseline   = RS409HBA&*
badtime1.type      = preflagger
badtime1.abstime   = 2015/12/13/15:16:02..2015/12/13/15:16:04
EOF
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'usrflag'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.badant.t${ts}.log 2>&1

#else

#echo "No parset with user flags found."

#fi

fi
################################## RFIFLAGGING  ####################################
if [ "$rfiflag" = true ];
then

PARSET=rfiflag.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = DATA
msout            =
steps            = [aoflag]
aoflag.type      = aoflagger
aoflag.autocorr  = FALSE
aoflag.strategy  = /cvmfs/softdrive.nl/lofar_sw/LOFAR/2.20.2/lofar/release/share/rfistrategies/HBAdefault
aoflag.memorymax = ${MMAX}
EOF
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'rfiflag1'

NDPPP ${PARSET} # > ${LOGS_DIR}/${LOGID}.rfiflag.t${ts}.log 2>&1
rm ${PARSET}

fi
################################## DEMIX       #####################################
MSOUT=$(printf '%s\n' "${MS%.MS}_dmx.MS")
if [ "$demix" = true ];
then
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'demixing'

PARSET=demix.t${ts}.parset
cat > ${PARSET} << EOF
msin                    = ${MS}
msin.datacolumn         = DATA
msout                   = ${MSOUT}
msout.datacolumn        = DATA
steps                   = [demixer]
demixer.skymodel        = ${ATEAM}
demixer.subtractsources = [CygA,CasA]
demixer.type            = demixer
demixer.freqstep        = 1
demixer.timestep        = 1
demixer.demixfreqstep   = 256 # One demix solution for whole SB
demixer.demixtimestep   = 20
EOF

NDPPP ${PARSET} # > ${LOGS_DIR}/${LOGID}.demix.t${ts}.log 2>&1
rm ${PARSET}

fi

# If a demixed version of the MS exists, use it
if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## RFIFLAGGING2  ####################################
if [ "$rfiflag2" = true ];
then

PARSET=rfiflag2.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = DATA
msout            =
steps            = [aoflag]
aoflag.type      = aoflagger
aoflag.autocorr  = FALSE
aoflag.strategy  = /cvmfs/softdrive.nl/lofar_sw/LOFAR/2.20.2/lofar/release/share/rfistrategies/HBAdefault
aoflag.memorymax = ${MMAX}
EOF

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'rfiflag2'

NDPPP ${PARSET} # > ${LOGS_DIR}/${LOGID}.rfiflag2.t${ts}.log 2>&1
rm ${PARSET}

fi
################################## AVERAGING    ####################################
MSOUT=$(printf '%s\n' "${MS%.MS}_avgt.MS")
if [ "$average_time" = true ];
then

PARSET=average_time.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = DATA
msout            = ${MSOUT}
msout.datacolumn = DATA
steps            = [avg]
avg.type         = average
avg.freqstep     = 1
avg.timestep     = 2
EOF

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'averaging'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.avgt.t${ts}.log 2>&1
rm ${PARSET}
fi

# If an averaged version of the MS exists, use it
if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi


MSOUT=$(printf '%s\n' "${MS%.MS}_avgf.MS")
if [ "$average_freq" = true ];
then

PARSET=average_freq.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = DATA
msout            = ${MSOUT}
msout.datacolumn = DATA
steps            = [avg]
avg.type         = average
avg.freqstep     = 4
avg.timestep     = 1
EOF

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.avgf.t${ts}.log 2>&1
rm ${PARSET}
fi

# If an averaged version of the MS exists, use it
if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## RFIFLAGGING3 ####################################
# Making a separate MS for the RFI flagged data after averaging does not use that
# much memory as making a copy before.
MSOUT=$(printf '%s\n' "${MS%.MS}_rfi3.MS")
if [ "$rfiflag3" = true ];
then

PARSET=rfiflag3.t${ts}.parset
cat > ${PARSET} << EOF
msin=${MS}
msin.autoweight  = FALSE
msin.datacolumn  = DATA
msout            = ${MSOUT}
msout.datacolumn = DATA
steps            = [aoflag]
aoflag.type      = aoflagger
aoflag.autocorr  = FALSE
aoflag.strategy  = /cvmfs/softdrive.nl/lofar_sw/LOFAR/2.20.2/lofar/release/share/rfistrategies/HBAdefault
aoflag.memorymax = ${MMAX}
EOF
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'rfiflag3'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.rfiflag3.t${ts}.log 2>&1
rm ${PARSET}

fi

# If a RFI flagged version of the MS exists, use it
if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## USER FLAGS  ####################################
if [ "$usrflag" = true ];
then

if [ -f ${FLAGPARSET} ];
then
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'usrflag'

NDPPP ${FLAGPARSET} msin=${MS} > ${LOGS_DIR}/${LOGID}.usrflag.t${ts}.log 2>&1

else

echo "No parset with user flags found."

fi

fi
################################## CALIBRATION #####################################
if [ "$calibrate" = true ];
then

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'calibrating'
if [ -d ${MS}/skymod ];
then
rm -rf ${MS}/skymod
fi

# Convert the skymodel to makesourcedb format
makesourcedb in=${MODEL} out=${MS}/skymod format='<'

PARSET=gaincal.t${ts}.parset
cat > ${PARSET} << EOF
msin                           = ${MS}
msin.autoweight                = FALSE
msin.datacolumn                = DATA
msout                          = ${MS}
msout.datacolumn               = DATA
steps                          = [gaincal]
gaincal.type                   = gaincal
gaincal.caltype                = ${CALTYPE}
gaincal.sourcedb               = ${MS}/skymod
gaincal.parmdb                 = ${PARMDB}
gaincal.maxiter                = 200
gaincal.sources                = [${SOURCES}]
gaincal.timeslotsperparmupdate = 500
gaincal.solint                 = 5
gaincal.propagatesolutions     = TRUE
gaincal.usebeammodel           = TRUE
EOF

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.gaincal.t${ts}.log 2>&1
rm ${PARSET}

# Plot solutions

fi
################################### CORRECTION ##########################################
if [ "$correct" = true ];
then

# Apply solutions
PARSET=applycal.t${ts}.parset
cat > ${PARSET} << EOF
msin                = ${MS}
msin.autoweight     = FALSE
msin.datacolumn     = DATA
msout               = ${MS}
msout.datacolumn    = CORRECTED_DATA
steps               = [applycal]
applycal.type       = applycal
applycal.correction = gain
applycal.parmdb     = ${PARMDB}
#applycal.timeslotsperparmupdate = 100000
EOF
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'applycal'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.applycal.t${ts}.log 2>&1
rm ${PARSET}

## set the parset and the model
#PARSET=calibrate.parset
#cat > ${PARSET} << EOF
#Strategy.ChunkSize                  = 0
#Strategy.InputColumn                = DATA
#Strategy.Steps                      = [correct]
#
#Step.correct.Model.Beam.Enable      = F
#Step.correct.Model.Gain.Enable      = T
#Step.correct.Model.Sources          = []
#Step.correct.Operation              = CORRECT
#Step.correct.Output.Column          = CORRECTED_DATA
#EOF

#calibrate-stand-alone -f ${MS} ${PARSET} ${MODEL} > ${LOGS_DIR}/${LOGID}.bbs.log 2>&1
#calibrate-stand-alone -t ${NCORES} --parmdb instrument_not_ph0 ${MS} ${PARSET} > ${LOGS_DIR}/${LOGID}.correct.t${ts}.log 2>&1

#rm ${PARSET}


fi
################################## RFIFLAGGING4  ####################################
MSOUT=$(printf '%s\n' "${MS%.MS}_rfi4.MS")

if [ "$rfiflag4" = true ];
then

PARSET=rfiflag4.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = CORRECTED_DATA
msout            = ${MSOUT}
msout.datacolumn = DATA
steps            = [aoflag]
aoflag.type      = aoflagger
aoflag.autocorr  = FALSE
aoflag.strategy  = /cvmfs/softdrive.nl/lofar_sw/LOFAR/2.20.2/lofar/release/share/rfistrategies/HBAdefault
aoflag.memorymax = ${MMAX}
EOF

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'rfiflag4'

NDPPP ${PARSET} #> ${LOGS_DIR}/${LOGID}.rfiflag4.t${ts}.log 2>&1
rm ${PARSET}

fi
# If a RFI flagged version of the MS exists, use it
if [ -d ${MSOUT} ];
then
MS=${MSOUT}
fi
################################## IMAGING     ####################################
IMAGE=$(printf '%s\n' "${MS%.MS}")

if [ "$cleanimag" = true ];
then

#awimager ms=${MS} image=${IMAGE}.CS.i10000.clean data=DATA weight=briggs robust=0 npix=256 \
#         cellsize=20arcsec padding=1. stokes=I operation=csclean oversample=5 niter=10000 threshold=0Jy \
#         wmax=20000 cyclefactor=1.5 gain=0.1 timewindow=300 antenna='CS*&' > ${LOGS_DIR}/${LOGID}.clean.t${ts}.log 2>&1


${wsclean} -j ${NCORES} -mem ${MMAX} -weight briggs ${ROBUST} -name ${IMAGE}.uvmax${MAXUV}.i${NITER}.r${ROBUST}.clean0 -size 512 512 -scale 5asec \
           -niter ${NITER} -threshold ${THRESHOLD} -mgain 0.85 -multiscale -multiscale-scales 0,9,18,36,72 -make-psf \
           -maxuv-l ${MAXUV} -apply-primary-beam -auto-mask 8 ${MS} #-auto-mask 8 ${MS} #-casamask casa_5asec_1024.mask ${MS}

fi

if [ -d ${MS}/model ];
then
rm -rf ${MS}/model
fi

if [ "$makemodel" = true ];
then

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'imaging'

CASASCRIPT=importfits.casapy
cat > ${CASASCRIPT} << EOF
importfits('${IMAGE}.uvmax${MAXUV}.i${NITER}.r${ROBUST}.clean0-model-pb.fits', '${IMAGE}.uvmax${MAXUV}.i${NITER}.r${ROBUST}.clean0-model-pb.image')
EOF

casa --nogui -c ${CASASCRIPT}
rm ${CASASCRIPT}
if [ -f *.last ];
then
rm *.last casa*.log ipython*.log
fi

casapy2bbs.py ${IMAGE}.uvmax${MAXUV}.i${NITER}.r${ROBUST}.clean0-model-pb.image ${NEWMOD}
makesourcedb in=${NEWMOD} out=${MS}/model format='<'

fi

if [ "$subtract" = true ];
then

PARSET=subtract.t${ts}.parset
cat > ${PARSET} << EOF
msin                    = ${MS}
msin.autoweight         = FALSE
msin.datacolumn         = DATA
msout                   = .
msout.datacolumn        = SUBTRACTED_MODEL
steps                   = [predict]
predict.type            = predict
predict.sourcedb        = ${MS}/model
predict.operation       = subtract
#predict.applycal.parmdb = ${PARMDB}
predict.usebeammodel    = TRUE
EOF

NDPPP ${PARSET} > ${LOGS_DIR}/${LOGID}.subtract.t${ts}.log 2>&1
rm ${PARSET}

PARSET=rfiflagsub.t${ts}.parset
cat > ${PARSET} << EOF
msin             = ${MS}
msin.autoweight  = FALSE
msin.datacolumn  = SUBTRACTED_MODEL
msout            = .
steps            = [aoflag]
aoflag.type      = aoflagger
aoflag.autocorr  = FALSE
aoflag.strategy  = default.rfis
aoflag.memorymax = ${MMAX}
EOF

NDPPP ${PARSET} > ${LOGS_DIR}/${LOGID}.rfiflagsub.t${ts}.log 2>&1
rm ${PARSET}

${wsclean} -j ${NCORES} -mem 30 -weight briggs ${ROBUST} -name ${IMAGE}.uvmax${MAXUV}.i${NITER}.clean1 -size 256 256 -scale 20asec \
           -niter ${NITER} -threshold 0 -auto-mask 8 -mgain 0.85 -multiscale -multiscale-scales 0,4,8,12,19 -make-psf \
           -maxuv-l ${MAXUV} -apply-primary-beam -datacolumn DATA ${MS}

fi
