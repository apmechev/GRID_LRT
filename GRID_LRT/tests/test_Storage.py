"""Testing Storage functions; For now just test imports. 
Need to scaffold test suite using mocked uberftp -ls results"""

from  GRID_LRT.storage.gsifile import GSIFile 
import unittest

class GSIFileTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creating_GSIFile(self):
        ''' Tests creating folders on the FS in the appropriate locations
        '''
        pass

    def test_autobuild(self):
        pass


if __name__ == '__main__':
    unittest.main()

