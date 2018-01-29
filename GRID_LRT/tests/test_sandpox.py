import GRID_LRT.sandbox as sandbox
import os 
import glob
import unittest

class SandboxTest(unittest.TestCase):

    def setUp(self):
        self.PWD=os.getcwd()
        self.sbxconf=os.getcwd()+'/config/steps/test.cfg'
#        os.chdir(self.PWD+"/GRID_LRT/Sandbox")


    def tearDown(self):
        for filename in glob.glob(self.PWD+'/GRID_LRT/Sandbox/*tar'):
            os.remove(filename)
#        os.chdir(self.PWD)

    def test_creating_folder(self):
        ''' Tests creating folders on the FS in the appropriate locations
        ''' 
        s=sandbox.Sandbox()
        s.parseconfig(self.sbxconf)
        s.create_SBX_folder()
        SBX_dir=s.sbx_def['name'] 
        self.assertTrue(os.path.exists(SBX_dir) & os.path.isdir(SBX_dir))
        s.cleanup()

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
