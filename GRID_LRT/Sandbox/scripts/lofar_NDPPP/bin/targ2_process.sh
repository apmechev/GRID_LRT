#!/bin/bash

function runtaql(){

    echo "running taql on "$( ls -d *${OBSID}*SB*  )"/SPECTRAL_WINDOW"
    FREQ=$( echo "select distinct REF_FREQUENCY from $( ls -d *${OBSID}*SB* )/SPECTRAL_WINDOW"| taql | tail -2 | head -1)
    A_SBN=$( $OLD_PYTHON update_token_freq.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} ${FREQ} )
    echo "Frequency is "${FREQ}" and Absolute Subband is "${A_SBN}
    mv prefactor/results/L*ms ${RUNDIR}  #moves untarred results from targ1 to ${RUNDIR} 



}

