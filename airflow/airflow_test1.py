from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.lofar_staging import LOFARStagingOperator
from airflow.contrib.operators.LRT_Sandbox import LRTSandboxOperator
from airflow.contrib.operators.LRT_token import TokenCreator,TokenUploader,ModifyTokenStatus
from airflow.contrib.operators.LRT_submit import LRTSubmit 
from airflow.contrib.sensors.glite_wms_sensor import gliteSensor
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
import pdb

default_args = {
    'owner': 'apmechev',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email': ['apmechev@gmail.com'],
    'email_on_failure': False, 
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'provide_context': True
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

def get_sbx_name(**kwargs):
    ti = kwargs['ti']
    return ti.xcom_pull(task_ids='stage_cal')

dag = DAG('Calib', default_args=default_args, schedule_interval='@once', catchup=False)

#####################################
#######Calibrator 1 block
#####################################

#Stage the files from the srmfile
stage = LOFARStagingOperator( task_id='stage_cal',
        srmfile='/home/apmechev/test/GRID_LRT/srm_L583139',
        dag=dag)

#Create a sandbox for the job
sandbox_cal = LRTSandboxOperator(task_id='sbx',
        sbx_config='/home/apmechev/test/GRID_LRT/config/sandboxes/test.cfg',
        dag=dag)

#Create the tokens and populate the srm.txt 
tokens_cal = TokenCreator(task_id='token_cal',
        sbx_task='sbx',
        staging_task ='stage_cal',
        tok_config ='/home/apmechev/test/GRID_LRT/config/tokens/pref_cal1.cfg',
        files_per_token=1,
        dag=dag)

#Upload the parset to all the tokens
parset_cal = TokenUploader(task_id='cal_parset', 
        token_task='token_cal',
        upload_file='/home/apmechev/test/GRID_LRT/parsets/Pre-Facet-Calibrator-1.parset',
        dag=dag)

#Reset the error tokens 
reset_err = ModifyTokenStatus(task_id='reset_error_tokens',
        token_task='token_cal',
        modification={'reset':'error'},
        dag=dag) 

reset_locked = ModifyTokenStatus(task_id='reset_lock_tokens',
                token_task='token_cal',
                        modification={'delete':'todo'},
                                dag=dag) 

#Reset done tokens
reset_done = ModifyTokenStatus(task_id='reset_done_tokens',
        token_task='token_cal',
        modification={'reset':'done'},
        dag=dag) 

#Submit tokens to the GRID
submit_cal = LRTSubmit(task_id='submit',
        token_task='token_cal',
        NCPU=2,
        dag=dag)

#Wait for all jobs to finish
wait_for_run_cal = gliteSensor(task_id='running',
        submit_task='submit',
        success_threshold=0.9,
        poke_interval=120,
        dag=dag)
        
#####################################
#######Calibrator 2 block
#####################################

sandbox_cal2 = LRTSandboxOperator(task_id='sbx_cal2',
        sbx_config='/home/apmechev/test/GRID_LRT/config/sandboxes/test2.cfg',
        dag=dag)

tokens_cal2 = TokenCreator( task_id='token_cal2',
        staging_task='stage_cal',
        sbx_task='sbx_cal2',
        files_per_token=300,
        tok_config='/home/apmechev/test/GRID_LRT/config/tokens/pref_cal2.cfg',
        dag=dag)

parset_cal2 = TokenUploader( task_id='cal_parset2',
        token_task='token_cal2',
        upload_file='/home/apmechev/test/GRID_LRT/parsets/Pre-Facet-Calibrator-2.parset', 
        dag=dag)

submit_cal2 = LRTSubmit( task_id='submit_cal2',
        token_task='token_cal2',
        NCPU=8,
        dag=dag)

wait_for_run_cal2 = gliteSensor( task_id='running_cal2',
        submit_task='submit_cal2',
        success_threshold=0.9,
        poke_interval=120,
        dag=dag)


#####################################
#######Target 1 block
#####################################


## Setting up the dependancy graph of the workflow
stage>>sandbox_cal>>tokens_cal>>parset_cal>>reset_err>>reset_done>>submit_cal>>wait_for_run_cal

wait_for_run_cal>>sandbox_cal2>>tokens_cal2>>parset_cal2>>submit_cal2>>wait_for_run_cal2



