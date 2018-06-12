from GRID_LRT import get_picas_credentials as get_pc
import os 
import glob
import unittest
try:
    import StringIO
except ImportError:
    import io.StringIO as StringIO



class picas_cred_test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass
    @unittest.mock.patch('sys.stdout', new_callable=StringIO)
    def test_info_logging(self):
        get_pc.infolog('infolog')
        self.assertEqual(mock_stdout.getvalue(), 'infolog')

    @unittest.mock.patch('sys.stdout', new_callable=StringIO)
    def test_debug_logging(self):
        get_pc.debuglog('debuglog')
        self.assertEqual(mock_stdout.getvalue(), 'debuglog')

    @unittest.mock.patch('sys.stdout', new_callable=StringIO)
    def test_warn_logging(self):
        get_pc.warnlog('warnlog')
        self.assertEqual(mock_stdout.getvalue(), 'warnlog')
        

if __name__ == '__main__':
    unittest.main() 
