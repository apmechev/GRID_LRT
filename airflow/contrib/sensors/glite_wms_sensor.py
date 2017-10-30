from __future__ import print_function
from future import standard_library
standard_library.install_aliases()
from builtins import str
from past.builtins import basestring

from datetime import datetime
import logging
from urllib.parse import urlparse
from time import sleep
import re
import sys
import subprocess
import pdb

import airflow
from airflow import hooks, settings
from airflow.exceptions import AirflowException, AirflowSensorTimeout, AirflowSkipException
from airflow.models import BaseOperator, TaskInstance
from airflow.hooks.base_hook import BaseHook
from airflow.hooks.hdfs_hook import HDFSHook
from airflow.utils.state import State
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults


class gliteSensor(BaseSensorOperator):
    """
    Runs a sql statement until a criteria is met. It will keep trying until
    sql returns no row, or if the first cell in (0, '0', '').

    :param conn_id: The connection to run the sensor against
    :type conn_id: string
    :param sql: The sql to run. To pass, it needs to return at least one cell
        that contains a non-zero / empty string value.
    """
    template_fields = ()
    template_ext = ()
    ui_color = '#7c7287'

    @apply_defaults
    def __init__(self, 
            submit_task, 
            success_threshold=0.9, 
            poke_interval=120,
            timeout=60*60*24*4, 
            *args, **kwargs):
        self.submit_task= submit_task
        self.threshold=success_threshold
        super(gliteSensor, self).__init__(poke_interval=poke_interval,
                timeout=timeout, *args, **kwargs)

    def poke(self, context):
        self.jobID=context['task_instance'].xcom_pull(task_ids=self.submit_task)
        if self.jobID==None:
            raise RuntimeError("Could not get the jobID from the "+str(self.submit_task)+" task. ")
        logging.info('Poking glite job: ' + self.jobID)
        g_proc = subprocess.Popen(['glite-wms-job-status', self.jobID] ,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        g_result=g_proc.communicate()
        self.parse_glite_jobs(g_result[0])
        if not 'Done' in self.job_status:
            return False
        else:
            exit_codes=self.count_successes(g_result[0])
            success_rate=exit_codes.count('0')/float(len(exit_codes))
            logging.info(str(success_rate)+" of jobs completed ok")
            if (success_rate < self.threshold):
                logging.error("Less than "+str(self.threshold)+" jobs finished ok!")
                raise RuntimeError("Not enough jobs completed ok on the grid! Only "+str(exit_codes.count('0'))+" jobs completed ok")
            return True

    def parse_glite_jobs(self,jobs): 
        self.job_status=jobs.split('Current Status:')[1].split()[0]
        logging.debug("Current job status is "+str(self.job_status))

    def count_successes(self,jobs):
        exit_codes=[] 
        for job_result in jobs.split('Exit code:'):
            exit_codes.append(job_result.split()[0])
        return exit_codes[2:]
        
