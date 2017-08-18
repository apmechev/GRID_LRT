#!/bin/bash

function run_pipeline(){


echo ""
echo "execute generic pipeline"

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'starting_imaging'
echo "Running ddf pipeline"

mkdir -p logs
$OLD_PYTHON update_token_progress.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} logs dummy.parste &

./ddf-pipeline/scripts/make_mslists.py
python ddf-pipeline/scripts/pipeline.py parset.cfg &> output

cat *mslist* >>log
cat output
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'processing_finished'




}
