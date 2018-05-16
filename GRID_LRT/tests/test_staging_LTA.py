from GRID_LRT.Staging import stage_all_LTA 
#from GRID_LRT.Staging import stager_access
import os
import glob
import unittest
import tempfile
from os.path import expanduser




class Staging_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        if not hasattr(self,'temfile'):
            return
        if self.temfile:
            with open(expanduser("~/.awe/Environment.cfg"),'w') as a_file:
                with open(self.temfile.name,'r') as f2:
                    for line in f2:
                        a_file.write(line)

    def test_stage_file(self):
        f=os.path.dirname(__file__)+'/srm_50_sara.txt'
        stage_all_LTA.main(f, test=True)

    def test_return_srmlist(self):
        f=os.path.dirname(__file__)+'/srm_50_sara.txt'
        l=stage_all_LTA.return_srmlist(f)
        self.assertTrue(len(l)==51)

    def test_awe_file(self):
        if os.path.exists(expanduser("~/.awe/Environment.cfg")):
            self.temfile=tempfile.NamedTemporaryFile(delete=False)
            with open(expanduser("~/.awe/Environment.cfg"),'r') as a_file:
                for line in a_file.readlines():
                    self.temfile.write(line)
            self.temfile.close()
        else:
            self.temfile=None
        with open(expanduser("~/.awe/Environment.cfg"),'w') as a_file:
            a_file.write("database_user : test1")
            a_file.write("database_password : test2")
        from GRID_LRT.Staging import stager_access
        self.assertTrue(stager_access.user=='test1')
        self.assertTrue(stager_access.password=='test2')


