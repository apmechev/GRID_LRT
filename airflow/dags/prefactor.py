from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.lofar_staging import LOFARStagingOperator
from airflow.contrib.operators.LRT_Sandbox import LRTSandboxOperator
from airflow.contrib.operators.LRT_token import TokenCreator,TokenUploader,ModifyTokenStatus
from airflow.contrib.operators.LRT_submit import LRTSubmit 
from airflow.contrib.operators.data_staged import Check_staged
from airflow.contrib.sensors.glite_wms_sensor import gliteSensor
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators.LRT_storage_to_srm import Storage_to_Srmlist 
from airflow.models import Variable

#Import helper fucntions 
from airflow.utils.AGLOW_utils import get_next_field
from airflow.utils.AGLOW_utils import count_files_uberftp 
from airflow.utils.AGLOW_utils import count_grid_files
from airflow.utils.AGLOW_utils import stage_if_needed

from GRID_LRT.Staging.srmlist import srmlist
import subprocess
import  fileinput
import logging
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


dag = DAG('SKSP_Prefactor', default_args=default_args, schedule_interval='0 */4 * * *' , catchup=False)

field_name='airflow_'
fields_file='/home/timshim/GRID_LRT2/GRID_LRT/SKSP/fields.txt'

#links to srmfiles are set as variables in the airflow UI 
calibsrmfile = Variable.get("SKSP_Calibrator_srm_file") 
targsrmfile = Variable.get("SKSP_Target_srm_file")

    
branch_if_cal_exists = BranchPythonOperator(
    task_id='branch_if_cal_processed',
    provide_context=True,                   # Allows to access returned values from other tasks
    python_callable=count_grid_files,
    op_args=[calibsrmfile,'check_calstaged','calib_done'
        "SKSP",'pref_cal1',1],         
    dag=dag)

branching_cal = BranchPythonOperator(
    task_id='branch_if_staging_needed',
    provide_context=True,                   # Allows to access returned values from other tasks
    python_callable=stage_if_needed,
    op_args=['check_calstaged','files_staged','stage_cal'],
    dag=dag)

files_staged = DummyOperator(
    task_id='files_staged',
    dag=dag
)   

calib_done = DummyOperator(
    task_id='calib_done',          
    dag=dag
)   

join = DummyOperator(
    task_id='join',
    trigger_rule='one_success',
    dag=dag
)   


#####################################
#######Calibrator 1 block
#####################################

#Stage the files from the srmfile
stage = LOFARStagingOperator( task_id='stage_cal',
        srmfile=calibsrmfile,
        dag=dag)

chk_stg_cal= Check_staged( task_id='check_calstaged' ,
        srmfile=calibsrmfile,
        dag=dag)

#Create a sandbox for the job
sandbox_cal = LRTSandboxOperator(task_id='sbx',
        sbx_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_cal1.cfg',
        dag=dag)

#Create the tokens and populate the srm.txt 
tokens_cal = TokenCreator(task_id='token_cal',
        sbx_task='sbx',
        staging_task ='check_calstaged',
        token_type=field_name,
        tok_config ='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_cal1.cfg',
        files_per_token=1,
        dag=dag)

#Upload the parset to all the tokens
parset_cal = TokenUploader(task_id='cal_parset', 
        token_task='token_cal',
        upload_file='/home/apmechev/GRIDTOOLS/GRID_LRT/parsets/Pre-Facet-Calibrator-1.parset',
        dag=dag)


#Submit tokens to the GRID
submit_cal = LRTSubmit(task_id='submit',
        token_task='token_cal',
        parameter_step=1,
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
        sbx_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_cal2.cfg',
        dag=dag)

tokens_cal2 = TokenCreator( task_id='token_cal2',
        staging_task='check_calstaged',
        sbx_task='sbx_cal2',
        token_type=field_name,                                                                           
        files_per_token=300,
        tok_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_cal2.cfg',
        dag=dag)

parset_cal2 = TokenUploader( task_id='cal_parset2',
        token_task='token_cal2',
        upload_file='/home/apmechev/GRIDTOOLS/GRID_LRT/parsets/Pre-Facet-Calibrator-2.parset', 
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


branching_targ = BranchPythonOperator(       
    task_id='branch_targ_if_staging_needed',
    provide_context=True,                   # Allows to access returned values from other tasks
    python_callable=stage_if_needed,
    op_args=['check_targstaged','files_staged_targ','stage_targ'],
    dag=dag) 
    
files_staged_targ = DummyOperator(
    task_id='files_staged_targ',
    dag=dag
)
     
    
join_targ = DummyOperator(
    task_id='join_targ',
    trigger_rule='one_success',
    dag=dag
)   


stage_targ= LOFARStagingOperator( task_id='stage_targ',
        srmfile=targsrmfile,
        dag=dag)

chk_stg_targ= Check_staged( task_id='check_targstaged' ,
        srmfile=targsrmfile,
        dag=dag)

sandbox_targ1 = LRTSandboxOperator(task_id='sbx_targ1',
        sbx_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_targ1.cfg',
        trigger_rule='all_done',        # The task will start when parents are success or skipped 
        dag=dag)
        
tokens_targ1 = TokenCreator( task_id='token_targ1',
        staging_task='check_targstaged',
        sbx_task='sbx_targ1',
        token_cal_task='token_cal',
        token_type=field_name,
        files_per_token=1,
        tok_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_targ1.cfg',
        dag=dag)
        
parset_targ1 = TokenUploader( task_id='targ_parset1',
        token_task='token_targ1',
        upload_file='/home/apmechev/GRIDTOOLS/GRID_LRT/parsets/Pre-Facet-Target-1.parset',
        dag=dag)
        
submit_targ1 = LRTSubmit( task_id='submit_targ1',
        token_task='token_targ1',
        NCPU=4,
        dag=dag)
        
wait_for_run_targ1 = gliteSensor( task_id='running_targ1',
        submit_task='submit_targ1',
        success_threshold=0.95,
        poke_interval=120,
        dag=dag)


#####################################
#######Target 2 block
#####################################

targ2_srmlist_from_storage = Storage_to_Srmlist(task_id='srmlist_from_targ1',
        token_task='token_targ1',
        dag=dag)

sandbox_targ2 = LRTSandboxOperator(task_id='sbx_targ2',
        sbx_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_targ2.cfg',
        dag=dag)
        
tokens_targ2 = TokenCreator( task_id='token_targ2',
        staging_task='srmlist_from_targ1',
        sbx_task='sbx_targ2',
        token_type=field_name,                                                                           
        files_per_token=10,
        subband_prefix='AB',        
        tok_config='/home/apmechev/GRIDTOOLS/GRID_LRT/config/steps/pref_targ2.cfg',
        dag=dag)

parset_targ2 = TokenUploader( task_id='targ_parset2',
        token_task='token_targ2',
        upload_file='/home/apmechev/GRIDTOOLS/GRID_LRT/parsets/Pre-Facet-Target-2.parset',
        dag=dag)
        
submit_targ2 = LRTSubmit( task_id='submit_targ2',
        token_task='token_targ2',
        parameter_step=1,
        NCPU=6,
        dag=dag)

wait_for_run_targ2 = gliteSensor( task_id='running_targ2',
        submit_task='submit_targ2',
        success_threshold=0.95,
        poke_interval=120,
        dag=dag)


## Setting up the dependency graph of the workflow


#Branch if calibrator already processed
branch_if_cal_exists >> chk_stg_cal
branch_if_cal_exists >> calib_done >>sandbox_targ1

#checking if calibrator is staged
chk_stg_cal >>  branching_cal
branching_cal >> stage >> join
branching_cal >> files_staged >> join
                
join >> sandbox_cal 

sandbox_cal >> tokens_cal >> parset_cal >>  submit_cal >> wait_for_run_cal

wait_for_run_cal >> sandbox_cal2 >> tokens_cal2 >> parset_cal2 >> submit_cal2 >> wait_for_run_cal2

#checking if target is staged
chk_stg_targ >> branching_targ

branching_targ >> files_staged_targ >> join_targ
branching_targ >> stage_targ >> join_targ

join_targ >> sandbox_targ1 

wait_for_run_cal2 >> sandbox_targ1 >> tokens_targ1 >> parset_targ1 >> submit_targ1 >> wait_for_run_targ1

wait_for_run_targ1 >> targ2_srmlist_from_storage >> tokens_targ2

wait_for_run_targ1 >> sandbox_targ2 >> tokens_targ2 >> parset_targ2 >> submit_targ2 >> wait_for_run_targ2


