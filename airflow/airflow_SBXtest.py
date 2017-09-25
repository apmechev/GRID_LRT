from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.contrib.operators.LRT_Sandbox import LRTSandboxOperator
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

from airflow.contrib.operators.LRT_Sandbox import LRTSandboxOperator
c=LRTSandboxOperator(sbx_config='/home/apmechev/test/GRID_LRT/config/sandboxes/test.cfg',task_id='sbx')
c.execute('test_field')


