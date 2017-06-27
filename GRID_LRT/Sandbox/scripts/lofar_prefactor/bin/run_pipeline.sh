#!/bin/bash

function run_pipeline() {

cd $RUNDIR
echo ""
echo "execute generic pipeline"
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'starting_generic_pipeline'
$OLD_PYTHON update_token_progress.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} output ${PARSET} &

genericpipeline.py ${PWD}/${PARSET} -d -c pipeline.cfg > output  

#if [[ $? != 0 ]]; then
#    echo "Processing error"
#    exit 99
#fi

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'processing_finished'

}
