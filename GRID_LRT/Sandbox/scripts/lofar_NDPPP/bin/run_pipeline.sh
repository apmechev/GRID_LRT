#!/bin/bash

function run_pipeline(){


echo ""
echo "execute NDPPP_Parset named ${PARSET}"
$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'starting_NDPPP'
$OLD_PYTHON update_token_progress.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} output ${PARSET} &

chmod a+x ${PARSET}
NDPPP ${PARSET}
wait # without wait, traps aren't caught

$OLD_PYTHON update_token_status.py ${PICAS_DB} ${PICAS_USR} ${PICAS_USR_PWD} ${TOKEN} 'processing_finished'

}
