

function print_job_info(){

echo "j_info: Run Directory is "${RUNDIR}
echo "PWD is $(pwd)"

echo "j_info: Pipeline is ${PIPELINE}"
echo "j_info:" "INITIALIZATION OF JOB ARGUMENTS"
echo "j_info: jobdir = " ${JOBDIR}
echo "j_info: startSB = " ${STARTSB}
echo "j_info: numSB = " ${NUMSB}
echo "j_info: parset = " ${PARSET}
echo "j_info: OBSID =" ${OBSID}

}

