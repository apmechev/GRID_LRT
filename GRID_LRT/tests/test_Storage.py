"""Testing Storage functions; For now just test imports. 
Need to scaffold test suite using mocked uberftp -ls results"""

from  GRID_LRT.storage import gsifile
import unittest

output_sksp="""drwx------  1 lofsksp    lofsksp             512 Oct  8 10:44 archive
drwx------  1 lofsksp    lofsksp             512 Oct 17 20:33 CI
drwx------  1 lofsksp    lofsksp             512 May 10  2017 sksp_natalie
drwx------  1 lofsksp    lofsksp             512 Jul 26 11:50 distrib
drwx------  1 lofsksp    lofsksp             512 Sep 18 14:06 sandbox
drwx------  1 lofsksp    lofsksp             512 Feb  5  2018 LGPPP
drwx------  1 lofsksp    lofsksp             512 Jul 17 10:50 pipelines"""

output_sbx_test="""-r--------  1 lofsksp    lofsksp        80445440 Nov 17  2017 airflowtest1.tar
-r--------  1 lofsksp    lofsksp       125491200 Nov 13  2017 test_data.tar
-r--------  1 lofsksp    lofsksp        80435200 Oct  4  2017 josh_pref_cal2.tar
-r--------  1 lofsksp    lofsksp           30720 Sep 24 15:03 calib_tutorial.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 24  2017 pref_targ2.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 24  2017 pref_targ1.tar
-r--------  1 lofsksp    lofsksp       212295680 Jan 24  2018 travis_test.tar
drwx------  1 lofsksp    lofsksp             512 Jan 23  2018 leah
-r--------  1 lofsksp    lofsksp        80445440 Nov 23  2017 pref_cal1.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 23  2017 pref_cal2.tar
-r--------  1 lofsksp    lofsksp           30720 Feb  2  2018 tutorial.tar"""

output_one_file="""-r--------  1 lofsksp    lofsksp        80445440 Nov 17  2017 airflowtest1.tar"""



from mock import MagicMock

class GSIFileTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_1(self):
        ''' Tests creating folders on the FS in the appropriate locations
        '''
        Popen = gsifile.Popen
        Popen.communicate = MagicMock(return_value=(output_sbx_test,""))
        gf = gsifile.GSIFile('gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/testf/')
        self.assertTrue(gf.location == 'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/testf/')

    def test_autobuild(self):
        pass


if __name__ == '__main__':
    unittest.main()

