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


class Check_staged(BaseOperator):
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
            srmfile=None, 
            success_threshold=0.9, 
            timeout=60*60*24*4, 
            *args, **kwargs):
        if srmfile:
            self.srmfile=srmfile
        else:
            raise ValueError("srmfile not defined") 
        self.threshold=success_threshold
        super(Check_staged, self).__init__(timeout=timeout, *args, **kwargs)

    def execute(self, context):
        staging_statuses=self.parse_srm_statuses(self.srmfile)
        if self.count_successes > self.threshold:
            return self.srmfile
        return ''

    def check_srm_status(self,srm):
        g_proc = subprocess.Popen(['srmls','-l', srm] ,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out=g_proc.communicate()
        if out[1]!='':
            raise RuntimeError('srmls failed')
        result=[s for s in out[0].split('\n') if 'locality' in s][0]
        stage_status_index=result.index(':')+1
        return result[stage_status_index:]
                    

    def parse_srm_statuses(self,srmfile): 
        _list_of_statuses=[]
        for line in open(srmfile).readlines()[:20]:
            if line:
                _list_of_statuses.append(self.check_srm_status(line.split()[0]))
        return _list_of_statuses


    def count_successes(self,status_list):
        suc=sum(st=='ONLINE_AND_NEARLINE' for st in status_list)
        fail=sum(st=='NEARLINE' for st in status_list)
        return suc/float(suc+fail)
        
