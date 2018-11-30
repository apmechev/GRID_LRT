import os
import glob
import unittest
import tempfile
from os.path import expanduser
import sys

from GRID_LRT.Staging import stage_all
from GRID_LRT.Staging.srmlist import srmlist
from GRID_LRT.Staging.stage_all import gfal

from mock import MagicMock
from mock import patch 

#gfal = stage_all.gfal
#gfal.creat_context = MagicMock()
#gfal.gfal_init = MagicMock(return_value=(0,2,3))
#gfal.creat_context.bring_online = MagicMock(return_value=(None,0))
#gfal.gfal_prestage = MagicMock(return_value=(0,1,2))

class Staging_Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_load_srmlist(self):
        slist = srmlist()
        for i in open(os.path.dirname(__file__)+'/srm_50_sara.txt','r') :
            slist.append(i.strip('\r\n'))
        self.assertTrue(len(slist) == 51)
        stager = stage_all.LTA_Stager(srmlist=slist)
        self.assertTrue(len(stager.srmlist) == 51)

    @patch('GRID_LRT.Staging.stage_all.stage_srm')
    def test_mocked_stage(self, bring_online_mock):
        ret_val =  bring_online_mock.return_value
        ret_val = ('sfsfs','22')
        stage_all.main(os.path.dirname(__file__)+'/srm_50_sara.txt')
