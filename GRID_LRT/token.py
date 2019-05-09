# -*- coding: utf-8 -*-
#
# Copyright (C) 2016 Alexandar P. Mechev
# All rights reserved.
#
# This software is licensed as described in the file LICENSE.md, which
# you should have received as part of this distribution.

"""
.. module:: GRID_LRT.Token
   :platform: Unix
   :synopsis: Set of tools for manually and automatically creating tokens

.. moduleauthor:: Alexandar Mechev <LOFAR@apmechev.com>
.. note:: Will be renamed GRID_LRT.token to conform to python standards

>>> #Example creation of a token of token_type 'test'
>>> from GRID_LRT.auth.get_picas_credentials import picas_cred
>>> pc=picas_cred() #Gets picas_credentials
>>>
>>> from cloudant.client import CouchDB         
>>> from GRID_LRT.token import caToken #Token that implements the cloudant interface
>>> from GRID_LRT.token import TokenList
>>> client = CouchDB(pc.user,pc.password, url='https://picas-lofar.grid.surfsara.nl:6984',connect=True)
>>> db = client[pc.database]
>>> 'token_id' in db # Checks if database includes the token
>>> db['token_id'] #Pulls the token 
>>> tl = TokenList(database=db, token_type='token_type') #makes an empty list
>>> tl.add_view(TokenView('temp',"doc.type == \"{}\" ".format(tl.token_type))) # adds a view to the token
>>> for token in tl.list_view_tokens('temp'):
        tl.append(caToken(token_type=tl.token_type, token_id= token['_id'], database=db))
        # adds every token in view to the local list (only their ids)
>>> tl.fetch() #Fetch actual data for token in list
>>> t1 = caToken(database=db, token_type='restructure_test', token_id=token_id) #make a token (locally)
>>> t1.build(TokenJsonBuilder('/path/to/token/data.json'))
>>> t1.save() #upload to the database
>>> t1.add_attachment(attachment_name='attachment_name_in_db.txt',filename='/path/to/attachment/file') #Adds attachment to token
"""

from __future__ import print_function
import sys
import os
import shutil
import itertools
import time
import tarfile
import json
#from retrying import retry
from abc import ABCMeta, abstractmethod
import pdb

import mimetypes
import GRID_LRT
from couchdb.design import ViewDefinition
import couchdb
from cloudant import couchdb as cloudant_couchdb
from cloudant.design_document import DesignDocument
from cloudant import couchdb_admin_party
#from cloudant.client import CouchDB
from cloudant import couchdb as CaCouchClient
from cloudant.document import Document
from cloudant.error import CloudantArgumentError
from requests.exceptions import HTTPError

__version__ = GRID_LRT.__version__
__author__ = GRID_LRT.__author__
__license__ = GRID_LRT.__license__
__email__ = GRID_LRT.__email__
__copyright__ = GRID_LRT.__copyright__
__credits__ = GRID_LRT.__credits__
__maintainer__ = GRID_LRT.__maintainer__
__status__ = GRID_LRT.__status__

def get_all_design_docs(pcreds=None, srv="https://picas-lofar.grid.surfsara.nl:6984"):
    """Returns a list of design documents for the pcreds.databse on server=srv
    If pcreds are none, then we're adminparty and db is test_db"""
    kwargs={'connect':True, 'url':srv}
    if pcreds:
        user, passwd, dbn = pcreds.user, pcreds.password, pcreds.database
        connect_client = CaCouchClient
        kwargs['user'] = user
        kwargs['passwd'] = passwd
    else:
        user, passwd, dbn = None, None, "test_db"
        connect_client = couchdb_admin_party
    with connect_client(**kwargs) as client:
        database = client[dbn]
        ad = [doc for doc in database['_all_docs']['rows'] if '_design' in doc['id']]
    return [i['id'] for i in ad]


def reset_all_tokens(token_type, picas_creds, server="https://picas-lofar.grid.surfsara.nl:6984"):
    """ Resets all Tokens with the pc authorization
    """
    thandler = TokenHandler(t_type=token_type, srv=server,
                            uname=picas_creds.user, pwd=picas_creds.password,
                            dbn=picas_creds.database)
    thandler.load_views()
    for view in list(thandler.views):
        if view != 'overview_total':
            thandler.reset_tokens(view)


def purge_tokens(token_type, picas_creds, server="https://picas-lofar.grid.surfsara.nl:6984"):
    """Automated function to purge tokens authorizing with Picas_creds"""
    thandler = TokenHandler(t_type=token_type, srv=server,
                            uname=picas_creds.user, pwd=picas_creds.password,
                            dbn=picas_creds.database)
    thandler.load_views()
    thandler.purge_tokens()

class Token(dict):
    def __init__(self, token_type, token_id=None, **kwargs):
        self.__setitem__('type', token_type)
        if not token_id:
            self.__setitem__('_id',token_type)
        else: 
            self.__setitem__('_id',token_id)
        self.__setitem__('lock', 0)
        self.__setitem__('done', 0)

    def synchronize(self, db, prefer_local=False, upload=False):
        """Synchronizes the token with the database. 
        """
        remote_token = db[self['_id']]
        for k in set(list(remote_token.keys())+list(self.keys())):
            if prefer_local:
                remote_token[k] = self.get(k)
            else:
                self[k] = remote_token.get(k)
        if upload:
            self.upload(db) 

    def build(self,token_builder):
        data = token_builder.data
        self.update(data)

    def add_attachment(self):
        raise NotImplementedError

    def reset(self):
        self.__setitem__('lock', 0)
        self.__setitem__('done', 0)
        scrub_count = self.get('scrub_count', 0)
        self.__setitem__('scrub_count', scrub_count + 1)
        self.__setitem__('hostname', '')
        self.__setitem__('output', '')

class caToken(Token, Document):
    def __init__(self, database, token_type, **kwargs):
        Token.__init__(self, token_type=token_type, **kwargs)
        Document.__init__(self,database=database, **kwargs)
        self._document_id = self['_id']

    def add_attachment(self, filename, attachment_name):
        file_type = mimetypes.guess_type(filename)[0]
        self.put_attachment(attachment_name, file_type, open(filename,'r'))

    def get_all_attachments(self):
        """Gets all attachments from the remote token and saves them
        to a file with name ID-Attachment"""
        self.fetch()
        for attachment in self.get('__attachments'):
            if not self['_attachments'][attachment].get('content-type'):
                 data=self.get_attachment(attachment, attachment_type='text/plain')
            else:
                data=self.get_attachment(attachment)
        with open(self['_id']+"-"+attachment,'wb') as att_f:
            att_f.write(data) 

class TokenBuilder:
    __metaclass__ = ABCMeta
    """Creates a token"""
 
    @abstractmethod
    def _build(self):
        pass

    @property
    def data(self):
        return self._data


class TokenDictBuilder(TokenBuilder):
    def __init__(self, config_dict):
        self._build(config_dict)

    def _build(self,config_dict):
        self._build_from_dict(config_dict)

    def _build_from_dict(self, config_dict):
        self._data={}
        if "PicasApiVersion" in config_dict and config_dict["PicasApiVersion"]<0.5:
            raise RuntimeError("Unsupported PiCaS API version {0}", config_dict["PicasApiVersion"])
        self._data['config.json']={}
        _config = config_dict
        _variables={}

        if 'Token' in _config:
            if 'variables' in _config['Token']:
                _variables.update(_config['Token']['variables'])
                _config['variables'] = _config['Token']['variables']
                del _config['Token']['variables']
            self._data.update(_config['Token'])

        if 'Job' in _config and 'variables' in _config['Job']:
            self._data.update(_config['Job']['variables'])
        
        if 'variables' in _config:
            self._data['config.json']['variables']=_config['variables']
        if 'container' in _config:
            self._data['config.json']['container']=_config['container']
        if 'sandbox' in _config:
            self._data['config.json']['sandbox']=_config['sandbox']
    

class TokenJsonBuilder(TokenDictBuilder):
    """Reads a json config file and builds the 
    Token fields using the data in this file."""
    def __init__(self, config_file):
        self._build(config_file)

    def _build(self, config_file):
        _config = json.load(open(config_file))
        self._data={}
        self._build_from_dict(_config)


class TokenList(list):
    """A list of token that a Token can be appended to
    Includes upload and download functions to upload all the 
    local documents and to download the remote ones
    
    NOTE: Implement this in a composite pattern, to allow sublists
    where each sublist is the result of a view"""
    def __init__(self, token_type=None, database=None):
        self._token_ids = []
        self._design_doc = None
        self.__set_database(database)
        self.__set_token_type(token_type)



    def __set_token_type(self, token_type):
        self.token_type = token_type
        if token_type and self._database!=None:
                self.__set_design_doc()

    def __set_database(self, database):
        self._database = database

    def __set_design_doc(self):
        design_doc_name = '_design/{0}'.format(self.token_type)
        self._design_doc = DesignDocument(self._database, design_doc_name)
        if design_doc_name not in self._database:
            self._design_doc.save()
        self._design_doc.fetch()

    def add_attachment(self, filename, attachment_name):
        for token in self:
            try:
                token.add_attachment(filename, attachment_name)
            except HTTPError as e:
                print(e)
                if '404' in str(e):
                    token.save()
                    token.add_attachment(filename, attachment_name)



    def append(self, item):
        if isinstance(item, Token):
            if not self._database:
                self.__set_database(item._database) #Does this have a getter?
            if not self.token_type:
                self.__set_token_type(item['type'])
            elif item['type'] != self.token_type:
                raise TypeError("Appending token of wrong token type, {0} != {1}".format(
                                item['type'], self.token_type))
            if item['_id'] not in self._token_ids:
                self._token_ids.append(item['_id'])
            else:
                raise RuntimeError("token with id {0} already exists! You need unique '_id' fields ".format(
                    item['_id']))
            super(TokenList, self).append(item)
        elif isinstance(item, TokenList):
            for _id in item._token_ids:
                self._token_ids.append(_id)
            super(TokenList, self).append(item)
        else:
            raise TypeError("Cannot append item {0} as it's not a Token".format(item))

    def upload_all(self):
        """Uploads all tokens in the list. It will crash if the token already exists
        This also cannot be called if the tokens were created inside a context manager
        that has been exited. Best option is to create a persistent 'cloudant.client.CouchDB'
        object. """
        for token in self:
            token.save()
    
    def save(self):
        self.upload_all()

    def delete_all(self):
        for token in self:
            token.delete()

    def reset(self):
        for token in self:
            token.reset()

    def delete(self):
        self.delete_all(self) 

    def add_view(self, view):
        map_code = view.get_codes(self.token_type)[0]
        reduce_code = view.get_codes(self.token_type)[1]
        if self._design_doc: 
            try:
                self._design_doc.add_view(view.name, map_code, reduce_code)
            except CloudantArgumentError:
                self._design_doc.delete_view(view.name)
                self._design_doc.add_view(view.name, map_code, reduce_code)
            self._design_doc.save()

    def fetch(self):
        for token in self:
            token.fetch()

    def list_view_tokens(self, view_name):
        view = self._design_doc.get_view(view_name)
        if not view:
            return self 
        view_list = TokenList(token_type=self.token_type, database=self._database)
        for i in view.result:
            tok=caToken(database=self._database, token_type=self.token_type,token_id=i['id'])
            view_list.append(tok)
        view_list.fetch()
        return view_list

    def get_views(self):
        if self._design_doc:
            self._design_doc.fetch()
            return self._design_doc.list_views()

    def delete_views(self):
        for view in self.get_views():
            self._design_doc.delete_view(view)
        self._design_doc.save()


    def add_token_views(self):
        """Adds the todo, locked, error, done and overview_view 
        views that are standard for a PiCaS Token."""
        self.add_view(TokenView("todo", 'doc.lock ==  0 && doc.done == 0 '))
        self.add_view(TokenView("locked", 'doc.lock > 0 && doc.done == 0 ',
                                ('doc._id', 'doc.status')))
        self.add_view(TokenView("done", 'doc.status == "done"' ))
        self.add_view(TokenView("error", 'doc.status == "error" ', ('doc._id', 'doc.status')))
        self.add_view(TokenReduceView('overview_view'))

class TokenView(object):
    def __init__(self, name, condition, emit_values=('doc._id', 'doc._id')):
        self.name = name
        self.condition = condition
        self.emit_values = emit_values

    def _get_map_code(self, token_type):
        general_view_code = """function(doc) {{
   if(doc.type == "{0}") {{
      if({1}) {{
         emit({2}, {3});
      }} 
   }} 
}}
""".format(token_type,
           self.condition,
           self.emit_values[0],
           self.emit_values[1])
        return general_view_code

    def _get_reduce_code(self):
        return None
 
    def get_codes(self, token_type):
        return self._get_map_code(token_type), self._get_reduce_code()

class TokenReduceView(TokenView):
    def __init__(self, name, **kwargs):
        super(TokenReduceView, self).__init__(name, kwargs)

    def _get_map_code(self, token_type):
        overview_map_code = '''function(doc) {{
   if(doc.type == "{0}" )
     {{
       if (doc.lock == 0 && doc.done == 0){{
          emit('todo', 1);
       }}
       if(doc.lock > 0 && doc.status == 'downloading' ) {{
          emit('downloading', 1);
       }}
       if(doc.lock > 0 && doc.done > 0 && doc.output == 0 ) {{
          emit('done', 1);
       }}
       if(doc.lock > 0 && doc.output != 0 && doc.output != "" ) {{
          emit('error', 1);
       }}
       if(doc.lock > 0 && doc.status == 'launched' ) {{
          emit('waiting', 1);
       }}
       if(doc.lock > 0  && doc.done==0 && doc.status!='downloading' ) {{
          emit('running', 1);
      }}
     }}  
}}
'''.format(token_type)
        return overview_map_code

    def _get_reduce_code(self):
        overview_reduce_code = '''function (key, values, rereduce) {
   return sum(values);
}   
'''     
        return overview_reduce_code

class TokenHandler(object):
    """self.database.get("_design/""

    The TokenHandler class uses couchdb to create, modify and delete
    tokens and views, to attach files, or download attachments and to
    easily modify fields in tokens. It's initiated with the token_type,
    server, username, password and name of database.

    """
    def __init__(self, t_type="token",
                 srv="https://picas-lofar.grid.surfsara.nl:6984",
                 uname="", pwd="", dbn=""):
        """
        >>> #Example creation of a token of token_type 'test'
        >>> from GRID_LRT.auth.get_picas_credentials import picas_cred
        >>> pc=picas_cred() #Gets picas_credentials
        >>>
        >>> th=token.TokenHandler( t_type="test",
        srv="https://picas-lofar.grid.surfsara.nl:6984", uname=pc.user,
        pwd=pc.password, dbn=pc.database ) #creates object to 'handle' Tokens
        >>> th.add_overview_view()
        >>> th.add_status_views() #Adds 'todo', 'done', 'locked' and 'error' views
        >>> th.load_views()
        >>> th.views.keys()
        >>> th.reset_tokens(view_name='error') # resets all tokens in 'error' view
        >>> th.set_view_to_status(view_name='done','processed')
        """
        print("TokenHandler is no longer supported!")


    @staticmethod
    def _append_id(keys, app=""):
        """ Helper function that appends a string to the token ID"""
        keys["_id"] += app


    def del_view(self, view_name="test_view"):
        pass

    def remove_error(self):
        pass

    def add_attachment(self, token, filehandle, filename="test"):
        pass 

    def list_attachments(self, token):
        pass

    def get_attachment(self, token, filename, savename=None):
        pass

    def list_tokens_from_view(self, view_name):
        pass

    def archive_tokens_from_view(self, viewname, delete_on_save=False):
        pass

    def archive_tokens(self, delete_on_save=False, compress=True):
        pass

    def archive_a_token(self, tokenid, delete=False):
        pass

    def clear_all_views(self):
        pass

    def purge_tokens(self):
        pass

    def set_view_to_status(self, view_name, status):
        pass

class TokenSet(object):
    """ The TokenSet object can automatically create a group of tokens from a
    yaml configuration file and a dictionary. It keeps track internally of
    the set of tokens and allows users to batch attach files to the entire TokenSet or alter
    fields of all tokens in the set.

    """

    def __init__(self, th=None, tok_config=None):
        """ The TokenSet object is created with a TokenHandler Object, which is
        responsible for the interface to the CouchDB views and Documents. This also ensures
        that only one job type is contained in a TokenSet.

        Args:
            :param th: The TokenHandler associated with the job tokens
            :type th: GRID_LRT.Token.TokenHandler
            :param tok_config: Location of the token yaml file on the host FileSystem
            :type tok_config: str
            :raises: AttributeError, KeyError

        """
        self.thandler = th
        self.__tokens = []
        if not tok_config:
            self.token_keys = {}
        else:
            with open(tok_config, 'r') as optfile:
                self.token_keys = json.load(optfile)['Token']

    def create_dict_tokens(self, iterable={}, id_prefix='SB', id_append="L000000",
                           key_name='STARTSB', file_upload=None):
        """ A function that accepts a dictionary and creates a set of tokens equal to
            the number of entries (keys) of the dictionary. The values of the dict are
            a list of strings that may be attached to each token if the 'file_upload'
            argument exists.

            Args:
                :param iterable: The dictionary which determines how many tokens will be created.
                The values  are attached to each token
                :type iterable: dict
                :param id_append: Option to append the OBSID to each Token
                :type id_append: str
                :param key_name: The Token field which will hold the value of the dictionary's
                keys for each Token
                :type key_name: str
                :param file_upload: The name of the file which to upload to the tokens
                (typically srm.txt)
                :type file_upload: str

        """  # TODO: Check if key_name is inside token_keys!
        for key in iterable:
            keys = dict(itertools.chain(self.token_keys.items(), {
                key_name: str("%03d" % int(key))}.items()))
#            _=keys.pop('_attachments')
            pipeline = ""
            if 'PIPELINE_STEP' in keys:
                pipeline = "_"+keys['PIPELINE_STEP']
            token = self.thandler.create_token(
                keys, append=id_append+pipeline+"_"+id_prefix+str("%03d" % int(key)))
            if file_upload:
                with open('temp_abn', 'w') as tmp_abn_file:
                    for i in iterable[key]:
                        tmp_abn_file.write("%s\n" % i)
                with open('temp_abn', 'r') as tmp_abn_file:
                    self.thandler.add_attachment(token, tmp_abn_file, file_upload)
                os.remove('temp_abn')
            self.__tokens.append(token)

    def add_attach_to_list(self, attachment, tok_list=None, name=None):
        '''Adds an attachment to all the tokens in the TokenSet, or to another list
            of tokens if explicitly specified.
        '''
        if not name:
            name = attachment
        if not tok_list:
            tok_list = self.__tokens
        for token in tok_list:
            self.thandler.add_attachment(token, open(
                attachment, 'r'), os.path.basename(name))

    @property
    def tokens(self):
        self.update_local_tokens()
        return self.__tokens

    def update_local_tokens(self):
        self.__tokens = []
        self.thandler.load_views()
        for view in self.thandler.views.keys():
            if view != 'overview_total':
                for token in self.thandler.list_tokens_from_view(view):
                    self.__tokens.append(token['id'])

    def add_keys_to_list(self, key, val, tok_list=None):
        if not tok_list:
            tok_list = self.__tokens
        to_update = []
        for token in tok_list:
            document = self.thandler.database[token]
            document[key] = str(val)
            to_update.append(document)
        self.thandler.database.update(to_update)
