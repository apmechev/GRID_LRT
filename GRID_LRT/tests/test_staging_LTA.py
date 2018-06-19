from GRID_LRT.Staging import stage_all_LTA 
from GRID_LRT.Staging import stager_access
import os
import glob
import unittest
import tempfile
from os.path import expanduser
import sys



class Staging_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_stagingrc(self):
        user, passw, _ = stager_access.get_staging_creds()
        self.assertTrue(user == 'apmechev') 
        directory=expanduser("~/")
        if os.path.exists(expanduser("~/.stagingrc")):
            os.remove(expanduser("~/.stagingrc"))
        if os.path.exists(expanduser("~/.awe/Environment.cfg")):
            os.remove(expanduser("~/.awe/Environment.cfg"))
        with open(expanduser("~/.stagingrc"),'w') as st_file:
            st_file.write('user=test1\n')
            st_file.write('password=test2\n')
        user2, passw2, _ = stager_access.get_staging_creds()
        sys.stderr.write('username is '+user2)
#        self.assertTrue(user2 == 'test1')
#        self.assertTrue(passw2 == 'test2') 
        f=os.path.dirname(__file__)+'/srm_50_sara.txt'
        stage_all_LTA.main(f, test=True)
        f=os.path.dirname(__file__)+'/srm_50_sara.txt'
        l=stage_all_LTA.return_srmlist(f)
        self.assertTrue(len(l)==51)
        directory=expanduser("~/.awe/")
        if not os.path.exists(directory):
                os.makedirs(directory)
        with open(expanduser("~/.awe/Environment.cfg"),'w') as a_file:
            a_file.write("database_user : test1\n")
            a_file.write("database_password : test2\n")
        prev_usr=os.environ['PICAS_USR']
        os.environ['PICAS_USR']=''
        prev_pwd=os.environ['PICAS_USR_PWD']
        os.environ['PICAS_USR_PWD']=''
#        self.assertTrue(stager_access.user=='test1')
#        self.assertTrue(stager_access.password=='test2')
        os.environ['PICAS_USR']=prev_usr
        os.environ['PICAS_USR_PWD']=prev_pwd

    def test_prettyprint(self):
        dic = {'3':1234132, '2342':"string", 'boo':'boo2'}
        stager_access.prettyprint(dic)
