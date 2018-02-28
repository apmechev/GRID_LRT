# -*- coding: utf-8 -*-
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from builtins import bytes
import os
import os.path
import signal
from time import sleep
import logging
from subprocess import Popen, STDOUT, PIPE
from tempfile import gettempdir, NamedTemporaryFile

from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.utils.file import TemporaryDirectory
from airflow.utils.state import State
#import progressbar
from GRID_LRT import Token
from GRID_LRT import get_picas_credentials
from GRID_LRT.Staging.srmlist import srmlist
from GRID_LRT.Staging.srmlist import slice_dicts
import yaml

import pdb

class TokenCreator(BaseOperator):
    """
    Using a Token template input, this class creates the tokens for a LOFAR job
    The tokens are a set of documents that contain the metadata for each processing
    job as well as the job's progress, step completion times, and etc. 

    :param sbx_task: The name of the sandbox task which passes the sbx_loc to the tokens
    :type sbx_task: string
    :param srms: a list of the srms that need to be staged
    :type srms: list
    :param stageID: In case staging was already done
    :type stageID: string
    :type output_encoding: output encoding of bash command
    """
    template_fields = ()
    template_ext = ()
    ui_color = '#f3f92c'

    @apply_defaults
    def __init__(
            self,
            tok_config,
            sbx_task,
            staging_task,
            token_cal_task=None,
            subband_prefix='SB',
            token_type='test_',
            files_per_token=10,
            output_encoding='utf-8',
            *args, **kwargs):

        super(TokenCreator, self).__init__(*args, **kwargs)
        self.tok_config = tok_config  
        self.sbx_task=sbx_task
        self.subband_prefix=subband_prefix
        self.staging_task=staging_task
        self.token_cal_task=token_cal_task
        self.files_per_token=files_per_token
        self.output_encoding = output_encoding
        self.t_type=token_type
        self.state=State.QUEUED

    def execute(self, context):
        """
        Execute the bash command in a temporary directory
        which will be cleaned afterwards
        """
        srms=self.get_staged_srms(context)
        if not srms:
            print("Could not get the list of staged srms!")
        pc=get_picas_credentials.picas_cred()
        tok_settings=yaml.load(open(self.tok_config,'rb'))['Token']
        pipe_type=tok_settings['PIPELINE']
        th=Token.Token_Handler(t_type=self.t_type+srms.OBSID,
                    uname=pc.user,pwd=pc.password,dbn=pc.database)
        th.add_overview_view()
        th.add_status_views()
        th.add_view(v_name=pipe_type, cond='doc.PIPELINE == "{0}" '.format(pipe_type))
        logging.info("Token settings are "+str(tok_settings))
        self.tokens=Token.TokenSet(th=th,tok_config=self.tok_config)
        self.upload_tokens(self.tokens)
        d=slice_dicts(srms.sbn_dict(pref=self.subband_prefix),self.files_per_token)
        self.tokens.create_dict_tokens(iterable=d,
                id_append=pipe_type,key_name='STARTSB',
                file_upload='srm.txt')
        self.tokens.add_keys_to_list("OBSID",srms.OBSID)
        
        if 'CAL_OBSID' in tok_settings.keys():
            cal_results=context['task_instance'].xcom_pull(task_ids=self.token_cal_task) 
            CAL_OBSID=cal_results['OBSID']
            self.tokens.add_keys_to_list("CAL_OBSID",CAL_OBSID)
        
        sbx_name=context['task_instance'].xcom_pull(task_ids=self.sbx_task)
        self.tokens.add_keys_to_list('SBXloc',"gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/"+sbx_name)
        return {'token_id': self.t_type+srms.OBSID, 
                'view': pipe_type,
                'OBSID': srms.OBSID}


    def upload_tokens(self,tokens):
        pass

    def upload_attachments(self,attachment):
        pass

    def modify_fields(self,field_dict):
        for k in field_dict.keys():
            self.tokens.add_keys_to_list(k,field_dict[k])

    def get_staged_srms(self,context):
        ti = context['task_instance']
        srm_xcom=ti.xcom_pull(task_ids=self.staging_task)['srmfile']
        logging.info("Srmfile is "+srm_xcom)
        if srm_xcom==None:
            raise RuntimeError("Could not get the srm list from the "+str(self.staging_task) +" task")
        self.srmlist=srmlist()
        for link in open(srm_xcom,'rb').readlines():
            self.srmlist.append(link)
        return self.srmlist

    def success(self):
        self.status=State.SUCCESS
        logging.info("Successfully uploaded " +
                    str(self.progress['Percent done']) + " % of the tokens.")
    
    def on_kill(self):
        logging.warn('Sending SIGTERM signal to staging group')
        self.state=State.SHUTDOWN
        os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)


class TokenUploader(BaseOperator):
    """
    Using a Token template input, this class creates the tokens for a LOFAR job
    The tokens are a set of documents that contain the metadata for each processing
    job as well as the job's progress, step completion times, and etc. 

    :param sbx_task: The name of the sandbox task which passes the sbx_loc to the tokens
    :type sbx_task: string
    :param srms: a list of the srms that need to be staged
    :type srms: list
    :param stageID: In case staging was already done
    :type stageID: string
    :type output_encoding: output encoding of bash command
    """ 
    template_fields = ()
    template_ext = ()
    ui_color = '#f0ede4'
            
    @apply_defaults
    def __init__(
            self,
            token_task, 
            upload_file='/home/apmechev/test/GRID_LRT/parsets/Pre-Facet-Calibrator-1.parset',
            output_encoding='utf-8',
            *args, **kwargs):
        
        super(TokenUploader, self).__init__(*args, **kwargs)
        self.token_task=token_task
        self.output_encoding = output_encoding
        self.upload_file=upload_file
        self.state=State.QUEUED

    def execute(self, context):
        """
        Execute the bash command in a temporary directory
        which will be cleaned afterwards
        """
        pc=get_picas_credentials.picas_cred()
        tok_dict=context['task_instance'].xcom_pull(task_ids=self.token_task)
        token_id=tok_dict['token_id']
        view=tok_dict['view']
        pc=get_picas_credentials.picas_cred()
        th=Token.Token_Handler(t_type=token_id,
                    uname=pc.user,pwd=pc.password,dbn=pc.database)
        self.tokens=th.list_tokens_from_view(view)
        for token in self.tokens:
            th.add_attachment(token.id,open(self.upload_file,'rb'),self.upload_file.split('/')[-1])
        

    def success(self):
        self.status=State.SUCCESS
        logging.info("Successfully uploaded " +
                    str(self.progress['Percent done']) + " % of the tokens.")

    def on_kill(self):
        logging.warn('Sending SIGTERM signal to staging group')
        self.state=State.SHUTDOWN
        os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)



class ModifyTokenStatus(BaseOperator):
    """
    Using a Token template input, this class creates the tokens for a LOFAR job
    The tokens are a set of documents that contain the metadata for each processing
    job as well as the job's progress, step completion times, and etc. 

    :param sbx_task: The name of the sandbox task which passes the sbx_loc to the tokens
    :type sbx_task: string
    :param srms: a list of the srms that need to be staged
    :type srms: list
    :param stageID: In case staging was already done
    :type stageID: string
    :type output_encoding: output encoding of bash command
    """ 
    template_fields = ()
    template_ext = () 
    ui_color = '#f0ede4'
             
    @apply_defaults
    def __init__(
            self,
            token_task,
            modification={'reset':'todo'}, #Dictionary of list of modifications
            output_encoding='utf-8',
            *args, **kwargs):
            
        super(ModifyTokenStatus, self).__init__(*args, **kwargs)
        self.token_task=token_task
        self.output_encoding = output_encoding
        self.modification=modification
        self.state=State.QUEUED
        
    def execute(self, context):
        """
        Execute the bash command in a temporary directory
        which will be cleaned afterwards
        """
        pc=get_picas_credentials.picas_cred()
        tok_dict=context['task_instance'].xcom_pull(task_ids=self.token_task)
        token_id=tok_dict['token_id']
        th=Token.Token_Handler(t_type=token_id,
                    uname=pc.user,pwd=pc.password,dbn=pc.database)        
        for operation, view in self.modification.iteritems():
            if operation=='reset':
                th.reset_tokens(view)
            if operation=='delete':
                th.delete_tokens(view)
            if operation=='set_to_status': # {'set_to_status':{"view":'view_name',"status":'status'}}
                th.set_view_to_status(view['view'],view['status'])

    def success(self):
        self.status=State.SUCCESS
        logging.info("Successfully uploaded " +
                    str(self.progress['Percent done']) + " % of the tokens.")
                    
    def on_kill(self):
        logging.warn('Sending SIGTERM signal to staging group')
        self.state=State.SHUTDOWN
        os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)
        
class ModifyTokenField(BaseOperator):
    """
    Using a Token template input, this class creates the tokens for a LOFAR job
    The tokens are a set of documents that contain the metadata for each processing
    job as well as the job's progress, step completion times, and etc. 

    :param sbx_task: The name of the sandbox task which passes the sbx_loc to the tokens
    :type sbx_task: string
    :param srms: a list of the srms that need to be staged
    :type srms: list
    :param stageID: In case staging was already done
    :type stageID: string
    :type output_encoding: output encoding of bash command
    """
    template_fields = ()
    template_ext = () 
    ui_color = '#f0ede4'

    @apply_defaults 
    def __init__(
            self,
            token_task,
            keyval=['CAL_OBSID','L123456'], #Dictionary of list of modifications
            output_encoding='utf-8',
            *args, **kwargs):
            
        super(ModifyTokenStatus, self).__init__(*args, **kwargs)
        self.token_task=token_task
        self.output_encoding = output_encoding
        self.modification=modification
        self.state=State.QUEUED
        
    def execute(self, context):
        """
        Execute the bash command in a temporary directory
        which will be cleaned afterwards
        """
        pc=get_picas_credentials.picas_cred()
        tok_dict=context['task_instance'].xcom_pull(task_ids=self.token_task)
        token_id=tok_dict['token_id']
        pc=get_picas_credentials.picas_cred()
        th=Token.Token_Handler(t_type=token_id,
                    uname=pc.user,pwd=pc.password,dbn=pc.database)
        ts=Token.Tokenset(th)
        ts.add_keys_to_list(key=keyval[0],val=keyval[1])

    def success(self):
        self.status=State.SUCCESS
        logging.info("Successfully modified the tokens.")
                    
    def on_kill(self):
        logging.warn('Sending SIGTERM signal to staging group')
        self.state=State.SHUTDOWN
        os.killpg(os.getpgid(self.sp.pid), signal.SIGTERM)


class SrmlistFromTokenView(BaseOperator):
    """
    A Token View returns a list of keys/values of (job description) documents
    that match the condition of the view. Using the data returned, we can create
    a srmlist of files stored by these tokens. This will srmlist can be passed
    to a future task to create tokens in chunks as required by the user

    """
    def __init__(
            self,
            token_task,
            view=['test'], 
            pattern='%s_%s', #this will make a srmlist of key_val
            output_encoding='utf-8',
            *args, **kwargs):
        
        super(ModifyTokenStatus, self).__init__(*args, **kwargs)
        self.token_task=token_task
        self.view=view
        self.pattern=pattern
        self.output_encoding = output_encoding
        self.state=State.QUEUED
        
    def execute(self, context):  
        tokens=self.get_tokens_from_view()
        f=NamedTemporaryFile(delete=False)
        surl_list=self.make_srmlist_from_token_list(tokens,
                pattern=self.pattern)
        for i in surl_list:
            f.write(i)

        return f.name

    def get_tokens_from_view(self):
        tokens=[]
        tok_dict=context['task_instance'].xcom_pull(task_ids=self.token_task)
        token_id=tok_dict['token_id']
        token_view=tok_dict['view'] #TODO: Decide if use view here or in initializer
        pc=get_picas_credentials.picas_cred()
        th=Token.Token_Handler(t_type=token_id,
                uname=pc.user,pwd=pc.password,dbn=pc.database)
        for t in th.list_tokens_from_view(token_view):
            tokens.append(t)
        return tokens

    def make_srmlist_from_token_list(self,token_list=[],pattern="%s_%s"):
        surl_list=srmlist.srmlist()
        for token in token_list:
            surl_list.append(pattern % (token['key'], token['value']))
        return surl_list
