import GRID_LRT.sandbox as sandbox
import os 
import glob
import unittest
import mock
import subprocess

def mocked_import():
    with mock.patch.object(subprocess, 'Popen') as mocked_popen:
        mocked_popen.return_value.returncode = 0
        mocked_popen.return_value.communicate.return_value = (str("the file really exists", 'utf-8'), str("",'utf-8'))
        s = sandbox.Sandbox()
    return s

class SandboxTest(unittest.TestCase):

    def setUp(self):
#        self.PWD=os.getcwd()
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+'/sandbox_config_NDPPP_from_git.cfg'))
        self.sbxconf=os.path.dirname(__file__)+'/sandbox_config_NDPPP_from_git.cfg'
#        os.chdir(self.PWD+"/GRID_LRT/Sandbox")


    def tearDown(self):
#        for filename in glob.glob(self.PWD+'/GRID_LRT/Sandbox/*tar'):
#            os.remove(filename)
#        os.chdir(self.PWD)
        pass


    def test_creating_folder(self):
        ''' Tests creating folders on the FS in the appropriate locations
        ''' 
        s = mocked_import()
        s.parseconfig(self.sbxconf)
        s.create_sbx_folder()
        sbx_dir=s.sbxloc
        self.assertTrue(os.path.exists(sbx_dir) & os.path.isdir(sbx_dir))
        s.cleanup()
        self.assertTrue(not((os.path.exists(sbx_dir))))

    def test_autobuild(self):
        s = mocked_import()
        s.build_sandbox(self.sbxconf)


#    def test_creating_deleting_sbx_yml(self):
#        '''Testing creating and deleting folders during cleanup
#        '''
#        s=sandbox.Sandbox()
#        s.parseconfig(self.sbxconf)
#        s.create_SBX_folder()
#        SBX_dir=s.options['sandbox']['name']
#        self.assertTrue(os.path.exists(SBX_dir) & os.path.isdir(SBX_dir))
#        s.cleanup()
#        self.assertFalse(os.path.exists(SBX_dir))
##
#    def test_check_sbx_upload(self):
#        ''' Tests gsiftp sandbox upload
#        '''
#        os.chdir(self.PWD+'/GRID_LRT/Sandbox')
#        s=sandbox.Sandbox()
#        s.parseconfig(self.sbxconf)
#        s.create_SBX_folder()
#        s.zip_SBX()
#        s.upload_SBX()
#        self.assertTrue(s.sandbox_exists(s.SBXloc)) 
#        s.delete_sandbox(s.SBXloc)
#        self.assertFalse(s.sandbox_exists(s.SBXloc))
#        s.cleanup()


if __name__ == '__main__':
    unittest.main() 
