from GRID_LRT.Staging.srmlist import srmlist
from GRID_LRT.Staging.srmlist import slice_dicts
import os 
import glob
import unittest



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
        self.assertTrue(sl[0]==sl[1])
        self.assertTrue(sl[0]==sl[2])

if __name__ == '__main__':
    unittest.main() 
