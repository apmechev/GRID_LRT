from GRID_LRT.application import submit
import os 
import glob
import unittest
import mock
import subprocess


def mocked_import(*args, **kwargs):
    with mock.patch.object(subprocess, 'Popen') as mocked_popen:
        mocked_popen.return_value.returncode = 0
        mocked_popen.return_value.communicate.return_value = (str("the file really exists", 'utf-8'), str("",'utf-8'))
        launcher = submit.JdlLauncher(*args, **kwargs)
    return launcher

class JdlsubmitTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_make_tempfile(self):
        launcher = mocked_import() 
        file_path = launcher.make_temp_jdlfile()
        self.assertTrue(os.path.exists(file_path.name))

    def test_launch_raises_error(self):
        launcher = mocked_import()
        l = launcher.make_temp_jdlfile()
        with launcher:
            self.assertRaises(OSError, launcher.launch) #Will raise OSerror if glite-wms-job-submit doesn't exist

    def test_default_args(self):
        launcher = mocked_import()
        self.assertTrue(launcher.numjobs==1)
        self.assertTrue(launcher.token_type=='t_test')
        self.assertTrue(launcher.ncpu==1)

    def test_Numjobs(self):
        launcher = mocked_import(NCPU=10)
        self.assertTrue(launcher.ncpu==10)
        jdl_file = launcher.build_jdl_file()
        self.assertTrue("CPUNumber = 10"in jdl_file)

    def test_LaunchFileExists(self):
        launcher = mocked_import(NCPU=10)
        jdl_file = launcher.build_jdl_file()
        self.assertTrue(os.path.exists(launcher.launch_file))
        self.assertTrue(os.path.isfile(launcher.launch_file))

if __name__ == '__main__':
    unittest.main() 
