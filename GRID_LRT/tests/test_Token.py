from GRID_LRT import Token 
from GRID_LRT.get_picas_credentials import picas_cred
import os
import glob
import unittest
import sys

vers=str(sys.version_info[0])+"."+str(sys.version_info[1])
T_TYPE="travis_ci_test"+vers
TOKEN="travis_getSBX_test"+vers


class TokenTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_create_Token(self):
        pc = picas_cred()
        th = Token.Token_Handler(t_type=T_TYPE, uname=pc.user, pwd=pc.password, dbn='test_db')
        self.assertTrue(th.get_db(uname=pc.user, pwd=pc.password,  dbn='test_db', 
            srv="http://localhost:5984/").name == 'test_db')
        th.create_token(keys={'test_suite':'Token'}, append="Tokentest", attach=[])
        th.add_status_views()
        th.add_overview_view()
        th.load_views()
        views = th.views

    def test_delete_token(self):
        pc = picas_cred()
        th = Token.Token_Handler(t_type=T_TYPE, uname=pc.user, pwd=pc.password, dbn='sksp_unittest')
        th.create_token(keys={'test_suite':'Token','lock':1}, append="Tokentest", attach=[])
        th.add_view('to_reset_view',cond=' doc.test_suite == "Token" ' )
        th.reset_tokens('to_reset_view')
        th.delete_tokens('to_reset_view')
        th.del_view('to_reset_view')
