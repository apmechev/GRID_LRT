from GRID_LRT.Staging.srmlist import srmlist, count_files_uberftp
from GRID_LRT.Staging.srmlist import slice_dicts

import os 
import glob
import unittest
import mock

output_sbx_test=bytes("""-r--------  1 lofsksp    lofsksp        80445440 Nov 17  2017 airflowtest1.tar
-r--------  1 lofsksp    lofsksp       125491200 Nov 13  2017 test_data.tar
-r--------  1 lofsksp    lofsksp        80435200 Oct  4  2017 josh_pref_cal2.tar
-r--------  1 lofsksp    lofsksp           30720 Sep 24 15:03 calib_tutorial.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 24  2017 pref_targ2.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 24  2017 pref_targ1.tar
-r--------  1 lofsksp    lofsksp       212295680 Jan 24  2018 travis_test.tar
drwx------  1 lofsksp    lofsksp             512 Jan 23  2018 leah
-r--------  1 lofsksp    lofsksp        80445440 Nov 23  2017 pref_cal1.tar
-r--------  1 lofsksp    lofsksp        80445440 Nov 23  2017 pref_cal2.tar
-r--------  1 lofsksp    lofsksp           30720 Feb  2  2018 tutorial.tar""".encode('ascii'))


class SrmlistTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_append_juelich1(self):
        sl=srmlist()
        self.assertTrue(sl.lta_location==None)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB010_uv.MS_c0a9adfa.tar")
        self.assertTrue(sl.lta_location=='juelich')
        self.assertTrue(sl[0]==sl[-1])
        self.assertTrue(sl[0]=="srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB010_uv.MS_c0a9adfa.tar")

    def test_append_poznan1(self):
        sl=srmlist()
        self.assertTrue(sl.lta_location==None)
        sl.append("srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lc6_004/555005/L555005_SB302_uv.MS_805a38ae.tar")
        self.assertTrue(sl.lta_location=='poznan')
        self.assertTrue(sl[0]==sl[-1])
        self.assertTrue(sl[0]=="srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lc6_004/555005/L555005_SB302_uv.MS_805a38ae.tar")

    def test_append_sara1(self):
        sl=srmlist()
        self.assertTrue(sl.lta_location==None)
        sl.append("srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc2_038/233700/L233700_SB290_uv.dppp.MS_83fc1cc3.tar")
        self.assertTrue(sl.lta_location=='sara')
        self.assertTrue(sl[0]==sl[-1])
        self.assertTrue(sl[0]=="srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc2_038/233700/L233700_SB290_uv.dppp.MS_83fc1cc3.tar")

    def test_gsiftp_sara(self):
        sl=srmlist()
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+'/srm_50_sara.txt'))
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as sfile:
            for line in sfile:
                self.assertTrue( line!="")
                self.assertTrue( line!=None)
                sl.append(line)
        self.assertTrue(len(sl)==51)
        gsiftps=[]
        for f in sl.gsi_links():
            self.assertTrue(f[:34]=='gsiftp://gridftp.grid.sara.nl:2811')
            gsiftps.append(f)
        self.assertTrue(len(gsiftps)==51)

    def test_append_juelichrepeat(self):
        sl=srmlist()
        self.assertTrue(len(sl)==0)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB010_uv.MS_c0a9adfa.tar")
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB010_uv.MS_c0a9adfa.tar")
        self.assertTrue(len(sl)==1)

    def test_append_juelich2(self):
        sl=srmlist()
        self.assertTrue(len(sl)==0)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB000_uv.MS_c0a9adfa.tar")
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB010_uv.MS_c0a9adfa.tar")
        self.assertTrue(len(sl)==2)

    def test_append_different_loc(self):
        sl=srmlist()
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB000_uv.MS_c0a9adfa.tar")
        self.assertRaises(AttributeError,sl.append, "srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lc6_004/555009/L555009_SB206_uv.MS_0a5d4f0d.tar")

    def test_readOBSID(self):
        sl=srmlist()
        self.assertTrue(sl.obsid==None)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB000_uv.MS_c0a9adfa.tar")
        self.assertTrue(sl.obsid=='L583127')

    def test_two_OBSIDs(self):
        sl=srmlist()
        self.assertTrue(sl.obsid==None)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB000_uv.MS_c0a9adfa.tar")
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB100_uv.MS_c0a9adfa.tar")
        self.assertRaises(AttributeError, sl.append, "srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L581127_SB000_uv.MS_c0a9adfa.tar")

    def test_parse_srmfile(self):
        pass

    def test_split_dict_1(self):
        sl=srmlist()
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+'/srm_50_sara.txt'))
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as sfile:
            for line in sfile:
                sl.append(line)
        self.assertTrue(len(sl)==51)
        s_dict=slice_dicts(sl.sbn_dict(),slice_size=1)
        self.assertTrue(len(s_dict.keys())==51)


    def test_split_dict_10(self):
        sl=srmlist()
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+'/srm_50_sara.txt'))
        with open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') as sfile:
            for line in sfile:
                sl.append(line)
        self.assertTrue(len(sl)==51)
        s_dict=slice_dicts(sl.sbn_dict(),slice_size=10)
        self.assertTrue(len(s_dict.keys())==6)

    def test_split_dict_10_with_prefix(self):
        sl=srmlist()
        self.assertTrue(os.path.exists(os.path.dirname(__file__)+'/dysco_test.txt'))
        with open(os.path.dirname(__file__)+'/dysco_test.txt','r') as sfile:
            for line in sfile:
                sl.append(line)
        self.assertTrue(len(sl)==25)
        s_dict=slice_dicts(sl.sbn_dict(pref='ABN_',suff='\.'),slice_size=25)
        self.assertTrue(len(s_dict.keys())==10)
    
    def test_trimming_spaces(self):
        sl=srmlist()
        sfile = "srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB100_uv.MS_c0a9adfa.tar"
        sl.append(sfile)
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB101_uv.MS_c0a9adfa.tar ")
        sl.append("srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB102_uv.MS_c0a9adfa.tar file://L583127_SB100_uv.MS_c0a9adfa.tar")
        self.assertTrue(sl[1]=="srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB101_uv.MS_c0a9adfa.tar")
        self.assertTrue(sl[2]=="srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB102_uv.MS_c0a9adfa.tar")

    def test_gfal_replace1(self):
        f_name = 'srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583127/L583127_SB100_uv.MS_c0a9adfa.tar'
        sl = srmlist(link=f_name)
        self.assertTrue(f_name == sl[0])
        g_link = sl.gfal_replace(sl[0])
        self.assertTrue('8443/srm/managerv2?SFN=' in sl.gfal_replace(sl[0]))

    def test_srm_replace(self):
        f_name = 'gsiftp://dcachepool12.fz-juelich.de:2811/pnfs/fz-juelich.de/data/lofar/ops/projects/lc7_012/583139/L583139_SB000_uv.MS_900c9fcf.tar'
        sl = srmlist(link=f_name)
        self.assertTrue(f_name == sl[0])
        srm_link = sl.srm_replace(sl[0])
        self.assertTrue('srm://lofar-srm.fz-juelich.de:8443' in sl.srm_replace(sl[0]))
        gsilink = sl.gsi_replace(sl.srm_replace(sl[0]))
        self.assertTrue(gsilink == f_name)

    def test_run_pozn(self):
        f_name = 'srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lc6_016/527613/L527613_SB228_uv.dppp.MS_90bafee7.tar'
        sl = srmlist(link=f_name)
        gsilink =sl.gsi_replace(sl[0])
        self.assertTrue('gsiftp://gridftp.lofar.psnc.pl:2811' in sl.gsi_replace(sl[0]))
        srm_link = sl.srm_replace(sl.gsi_replace(sl[0]))
        self.assertTrue(srm_link == f_name)

    @mock.patch('subprocess.Popen', autospec=True)
    def test_count_files(self,  mock_subproc_popen):
        from GRID_LRT.auth import grid_credentials
        process_mock = mock.Mock()
        attrs = {'communicate.return_value': (output_sbx_test, 'error')}
        process_mock.configure_mock(**attrs)
        mock_subproc_popen.return_value = process_mock
        files = count_files_uberftp('gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/')
        logging.warn(len(files))
        self.assertTrue(len(files)==10)


if __name__ == '__main__':
    unittest.main() 
