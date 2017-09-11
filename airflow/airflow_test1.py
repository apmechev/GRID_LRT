from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.lofar_staging import LOFARStagingOperator
from datetime import datetime, timedelta


default_args = {
    'owner': 'apmechev',
    'depends_on_past': False,
    'start_date': datetime.now(),
    'email': ['apmechev@gmail.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
}

dag = DAG('staging', default_args=default_args)

from airflow.contrib.operators.lofar_staging import LOFARStagingOperator
c=LOFARStagingOperator(srmfile='../srm_L582109',task_id='stage_cal')
c.execute('test_field')

