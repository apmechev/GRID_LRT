import random
import string
import os
import glob
import unittest
import sys
import json 

import GRID_LRT
from GRID_LRT import token
from GRID_LRT.token import TokenDictBuilder
from GRID_LRT.token import TokenJsonBuilder
from GRID_LRT.auth.get_picas_credentials import picas_cred

vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
T_TYPE="travis_ci_test"+vers
TOKEN="travis_getSBX_test"+vers
BASEPATH = GRID_LRT.__file__.split('__init__.py')[0]+'/'

class TokenTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_Token(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                 uname='', pwd="", dbn='test_db')
        self.assertTrue(th._get_db(uname='', pwd="",  dbn='test_db', 
            srv="http://localhost:5984/").name == 'test_db')
        th.create_token(keys={'test_suite':'Token'}, append="Tokentest", attach=[])
        th.add_status_views()
        th.add_overview_view()
        th.load_views()
        views = th.views
        self.assertTrue('todo' in views.keys())
        self.assertTrue('locked' in views.keys())
        self.assertTrue('error' in views.keys())
        self.assertTrue('done' in views.keys())
        self.assertTrue('overview_total' in views.keys())
        th.purge_tokens()

    def test_new_Token(self):
        t1 = token.Token(token_type='test')
        self.assertTrue('type' in t1)
        self.assertTrue('_id' in t1)
        self.assertEquals(t1['type'],'test')
        self.assertEquals(t1['_id'],'test')
    
    def test_new_Token_with_id(self):
        t1 = token.Token(token_type='test', token_id='my_id')
        self.assertTrue('type' in t1)
        self.assertTrue('_id' in t1)
        self.assertEquals(t1['type'],'test')
        self.assertEquals(t1['_id'],'my_id')
    
    def test_synchornize_Token(self):
        t1=token.Token(token_type='test')
        db={}
        db[t1['_id']]=t1
        t1.synchronize(db)
        self.assertEquals(t1, {'_id': 'test', 'type': 'test','lock': 0, 'done': 0})
        db[t1['_id']]['two']=2
        t1.synchronize(db)
        self.assertTrue('type' in t1)
        self.assertTrue('_id' in t1)
        self.assertTrue('two' in t1)
        t1=token.Token(token_type='test')
        t1.synchronize(db, prefer_local=True)
        self.assertTrue('two' not in t1)
        self.assertTrue('two' in db[t1['_id']])
        db[t1['_id']] = dict(t1)
        self.assertTrue('two' not in db[t1['_id']])

    def test_token_builder(self):
        t1=token.Token(token_type='test')
        t2=token.Token(token_type='test')
        config_path = "{0}/{1}".format(BASEPATH,'data/config/steps/cal_pref3.json')
        with open(config_path) as _jsonfile:
            data = json.load(_jsonfile)
            t1.build(TokenDictBuilder(data))
            t2.build(TokenJsonBuilder(config_path))
        for k in [u'status', u'upload', '_id', 'type', 'config.json', u'times']:
            self.assertTrue(k in t1)
            self.assertTrue(k in t2)


    def test_delete_token(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                 uname="", pwd="", dbn='test_db')
        th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':1}, append="Tokentest", attach=[])
        th.add_status_views()
        th.set_view_to_status(view_name='todo',status='locked')
        self.assertTrue(len(th.list_tokens_from_view('locked'))==1)
        self.assertTrue(len(th.list_tokens_from_view('todo'))==0)
        th.add_view('to_reset_view',cond=' doc.test_suite == "test_delete_token" ' )
        th.reset_tokens('locked')
        self.assertTrue(len(th.list_tokens_from_view('todo'))==1)
        self.assertTrue(len(th.list_tokens_from_view('locked'))==0)
        th.delete_tokens('todo')
        self.assertTrue(len(th.list_tokens_from_view('todo'))==0)
        th.del_view('to_reset_view')
        th.purge_tokens()

    def test_purge_tokens(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                 uname="", pwd="", dbn='test_db')
        th.create_token(keys={'test_suite':'Token','lock':1}, append="Tokentest", attach=[])
        th.add_status_views() #Note without this, purge crashes!
        pc=picas_cred()
        pc.user,pc.password="",""
        pc.database = 'test_db'
        token.purge_tokens(T_TYPE,pc, "http://localhost:5984/")

    def test_reset_tokens(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                uname="", pwd="", dbn='test_db')
        th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':1}, append="Tokentest", attach=[])
        th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':1}, append="Tokentest2", attach=[])
        th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':1}, append="Tokentest3", attach=[])
        th.add_status_views()
        th.set_view_to_status(view_name='todo',status='locked')
        pc=picas_cred()
        pc.user,pc.password="",""
        pc.database = 'test_db'
        token.reset_all_tokens(T_TYPE,pc, "http://localhost:5984/")
        self.assertTrue(len(th.list_tokens_from_view('locked'))==0)
        self.assertTrue(len(th.list_tokens_from_view('todo'))==3)

    def test_no_views(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                 uname="", pwd="", dbn='test_db')
        th.load_views()
        self.assertTrue(th.views == {})
    
    def test_attachments(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                uname="", pwd="", dbn='test_db')
        tok = th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':0}, append="Tokentest", attach=[])
        th.add_status_views()
#       tok = list(th.list_tokens_from_view('todo'))[0]['id']
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as test_att:
            th.add_attachment(tok, test_att, 'test')
        attaches = th.list_attachments(tok)
        self.assertTrue(len(attaches)==1)
        self.assertTrue(attaches[0]=='test')
        no_savename = th.get_attachment(tok,'test')
        savename = th.get_attachment(tok,'test',savename='not_a_test')
        self.assertTrue(no_savename.split('/')[-1]=='test')
        self.assertTrue(savename.split('/')[-1]=='not_a_test')
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as test_att:
            th.add_attachment(tok, test_att, 'test/with/slash')
        slash_name = th.get_attachment(tok,'test/with/slash')
        self.assertTrue(slash_name.split('/')[-1]=='test_with_slash')

    def test_archive_a_token(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                uname="", pwd="", dbn='test_db')
        tok = th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':0}, append="archiveme1", attach=[])
        dump = th.archive_a_token(tok)
        self.assertTrue(tok+'.dump' in dump)
        tok2 = th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':0}, append="archiveme2", attach=[])
        th.archive_a_token(tok2, delete=True)
        tok3 = th.create_token(keys={'test_suite':'test_delete_tokens','done':0,'lock':0}, append="archiveme3", attach=[])
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as test_att:
                th.add_attachment(tok3, test_att, 'test')
        dump2 = th.archive_a_token(tok3)
        self.assertTrue('test' in dump2)

    def test_get_all_design_docs(self):
        T_TYPE = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(10))
        th = token.TokenHandler(t_type=T_TYPE, srv="http://localhost:5984/",
                                uname="", pwd="", dbn='test_db') 
        th.add_status_views()
        th.add_overview_view()
        design_docs = token.get_all_design_docs(None, srv="http://localhost:5984")
        self.assertTrue(len(design_docs)>0)
        self.assertTrue('_design/'+T_TYPE in design_docs)
