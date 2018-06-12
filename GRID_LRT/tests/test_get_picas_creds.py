from GRID_LRT import get_picas_credentials as get_pc
import os 
import glob
import unittest
 



class picas_cred_test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass


    def test_info_logging(self):
        get_pc.infolog('infolog')



    def test_debug_logging(self):
        get_pc.debuglog('debuglog')



    def test_warn_logging(self):
        get_pc.warnlog('warnlog')

        

if __name__ == '__main__':
    unittest.main() 
