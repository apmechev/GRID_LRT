from GRID_LRT.auth import get_picas_credentials as get_pc
import os 
import glob
import unittest
import tempfile



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

    def test_get_pc_adapter_works(self):
        pc = get_pc.picas_cred()
        pc_fun = get_pc.get_picas_cred()
        self.assertTrue(pc.user==pc_fun.user)
        self.assertTrue(pc.password==pc_fun.password)
        self.assertTrue(pc.database==pc_fun.database)


    def test_get_cred_from_file(self):
        f = tempfile.NamedTemporaryFile(delete=False)
        with open(f.name,'w') as _file:
            _file.write('user=testuser\n')
            _file.write('password=testpasswd\n')
            _file.write('database=testdatabase\n')
        pc = get_pc.picas_cred(source_file=f.name)
        self.assertTrue(pc.user=='testuser')
        self.assertTrue(pc.password=='testpasswd')
        self.assertTrue(pc.database=='testdatabase')
        os.remove(f.name)

    def test_get_creds_from_init(self):
         pc = get_pc.picas_cred(usr='tusr', pwd='tpwd', dbn='tdb')
         self.assertTrue(pc.user=='tusr')
         self.assertTrue(pc.password=='tpwd')
         self.assertTrue(pc.database=='tdb')

    def test_get_creds_from_env(self):
        os.environ['PICAS_USR'] = 'picas_test_user'
        os.environ['PICAS_USR_PWD'] = 'picas_test_pass'
        os.environ['PICAS_DB'] = 'picas_test_db'
        pc = get_pc.picas_cred()
        self.assertTrue(pc.user=='picas_test_user')
        self.assertTrue(pc.password=='picas_test_pass')
        self.assertTrue(pc.database=='picas_test_db')


if __name__ == '__main__':
    unittest.main() 
