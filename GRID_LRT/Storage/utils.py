from datetime import datetime
from subprocess import Popen, PIPE
import re
import GRID_LRT.auth.grid_credentials as grid_creds

class GSIFile(object):
    def __init__(self, location):
        _ = grid_creds.grid_credentials_enabled()
        self._internal = self._test_file_exists(location)
        self.datetime = self._internal['datetime']
        self.location = self._internal['location']
        self.filename = self._internal['filename']
        self.protocol = location.split("://")[0]
        self.port = self._get_port(location)
        self.is_dir, self.parent_dir = self._check_if_directory(location)
        if self.is_dir:
            self.is_file = False
        else:
            self.is_file = True

    def _check_if_directory(self,location):
        num_subdir = len([i for i in location.split('/') if i]) #check if too deep
        filename = location.split('/')[-1]
        parent_dir = self.get_parent_dir()
        parent_dir = parent_dir.replace(self.protocol+':/',self.protocol+"://")  #TODO Make this cleaner (new staticmethod)
        sub = Popen(['uberftp','-ls',parent_dir], stdout=PIPE, stderr=PIPE)
        res, err = sub.communicate()
        status = [x for x in res.split('\r\n') if filename in x]
        if status[0][0]=='d':
            return True, parent_dir
        else:
            return False, parent_dir


    def _test_file_exists(self,location):
        sub = Popen(['uberftp','-ls',location], stdout=PIPE, stderr=PIPE)
        result, error = sub.communicate()
        if error:
            raise Warning("file %s cannot be found: %s"%(location, error))
            return {'location':None, 'datetime':None, 'filename':None, 'raw':None}
        result = result.split()
        datetime =self._extract_date(result)
        filename = result[-1]
        return {'location':location, 'datetime':datetime, 'filename':filename, 'raw':result}

    @staticmethod
    def _extract_date(data):
        if data[-2] not in ['2018','2017','2016','2015']:
            date = data[-4]+" "+data[-3]+" " + str(datetime.now().year)
            time = data[-2]
        else:
            date = data[-4]+" "+data[-3]+" "+data[-2]
            time = "00:00"
        file_datetime = datetime.strptime(date+"-"+time, "%b %d %Y-%H:%M")
        return file_datetime

    @staticmethod
    def _get_port(location):
        try:
            port = re.search(':[0-9]{4}/',location).group(0)[1:][:-1]
            return port
        except AttributeError:
            return None

    def _donotdelete(self,location):
        """Raises Exception if you try to delete files or folders whose parent is
        one of these folders"""
        locations = ['gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/archive',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/sksp_natalie',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/LGPPP',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/PiLL',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/test',
                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/NDPPP'
#                     'gsiftp://gridftp.grid.sara.nl/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/DISC'
                     ]
        if self.parent_dir in locations:
            raise Exception("Not allowed to delete this folder because its parent is %s" % (self.parent_dir))

    def delete(self):
        parent_dir = self.get_parent_dir()
        self._dontdelete(parent_dir)
    
    def get_parent_dir(self):
        location = "/".join([i for i in self.location.split('/') if i])
        parent_dir = "/".join(location.split('/')[:-1])
        return parent_dir
def remove_gsi_file(file_obj):
    
