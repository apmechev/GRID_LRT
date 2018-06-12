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

    def create_Token(self):
        pc=picas_cred()
        th=Token.TokenHandler(t_type=T_TYPE, uname=pc.user, pwd=pc.password, dbn='sksp_unittest')
        self.assertTrue(th.get_db(uname=pc.user, pwd=pc.password,  dbn='sksp_unittest', srv="https://picas-lofar.grid.surfsara.nl:6984").name=='sksp_unittest')
