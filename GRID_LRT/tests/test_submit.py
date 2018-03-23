from GRID_LRT.Application import submit
import os 
import glob
import unittest



class JdlsubmitTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_make_tempfile(self):
        launcher = submit.jdl_launcher()
        file_path = launcher.make_temp_jdlfile()
        self.assertTrue(os.path.exists(file_path))
    
    def test_launch_raises_error(self):
        launcher=submit.jdl_launcher()
        l = launcher.make_temp_jdlfile()
        self.assertRaises(RuntimeError, launcher.launch)

    def test_default_args(self):
        launcher=submit.jdl_launcher()
        self.assertTrue(launcher.numjobs==1)
        self.assertTrue(launcher.token_type=='t_test')
        self.assertTrue(launcher.NCPU==1)

    def test_Numjobs(self):
        launcher=submit.jdl_launcher(numjobs=10)
        self.assertTrue(launcher.numjobs==10)
        jdl_file=launcher.build_jdl_file()
        self.assertTrue("Parameters= 10" in jdl_file)

    def test_Numjobs(self):
        launcher=submit.jdl_launcher(NCPU=10)
        self.assertTrue(launcher.NCPU==10)
        jdl_file=launcher.build_jdl_file()
        self.assertTrue("CPUNumber = 10"in jdl_file)

    def test_LaunchFileExists(self):
        launcher=submit.jdl_launcher(NCPU=10)
        jdl_file=launcher.build_jdl_file()
        self.assertTrue(os.path.exists(launcher.launch_file))
        self.assertTrue(os.path.isfile(launcher.launch_file))

if __name__ == '__main__':
    unittest.main() 
