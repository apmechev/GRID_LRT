from GRID_LRT.Staging import stage_all
from GRID_LRt.Staging.srmlist import srmlist
import os
import glob
import unittest
import tempfile
from os.path import expanduser
import sys



class Staging_Test(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load_srmlist(self):
        slist = srmlist()
        for i in open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') :
            slist.append(i.strip('\r\n')
        self.assertTrue(len(slist) == 51)
        stager = stage_all.LTA_Stager(srmlist=slist)
        self.assertTrue(len(stager.srmlist) == 51)
