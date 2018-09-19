from datetime import datetime
import warnings
from subprocess import Popen, PIPE
import re
import GRID_LRT.auth.grid_credentials as grid_creds
from GRID_LRT.auth.get_picas_credentials import picas_cred
from GRID_LRT import Token
from GRID_LRT.Staging.srmlist import srmlist

import pdb
class GSIFile(object):
    def __init__(self, location, parent_dir=None):
#        _ = grid_creds.grid_credentials_enabled()
        if parent_dir:
            self._internal = parent_dir.split()
        else:
            self._internal = self._test_file_exists(location)
        self.datetime = self._extract_date(self._internal)
        self.location = location
        self.protocol = location.split("://")[0]
        self.port = self._get_port(location)
        if parent_dir:
            self.parent_dir = None
            if self._internal[0]=='d':
                self.is_dir = True
            else:
                self.is_dir = False
        else:
           self.is_dir, self.parent_dir = self._check_if_directory(location)
        if self.is_dir:
            self.is_file = False
            self.filename = self.location.split('/')[-1]
        else:
            self.is_file = True
            self.filename = self._internal[-1]


    def _check_if_directory(self,location):
        self.num_subdir = len([i for i in location.split('gsiftp://')[1].split('/') if i]) - 1
        filename = location.split('/')[-1]
        parent_dir = self.get_parent_dir()
        parent_dir = parent_dir.replace(self.protocol+':/',self.protocol+"://")  #TODO Make this cleaner (new staticmethod)
        res, err = self._uberftpls(parent_dir)
        if '550' in err:
            warnings.warn('Parent directory inaccessible!: {}'.format(err))
            return None, parent_dir #Doesn't know if it's a file or dir if can't get parent_dir
        status = [x for x in res.split('\r\n') if filename in x]
        if status[0][0]=='d':
            return True, parent_dir
        else:
            return False, parent_dir

    def __repr__(self):
        return "<GRID_LRT.Storage.utils.GSIFile {} {} located in {} >".format("File" if self.is_file else "Folder", 
                self.filename, self.location)

    def _test_file_exists(self,location):
        result, error = self._uberftpls(location)
        if result=="" and error=="":
            if location[-1]=='/':
                location = location[:-1]
                result, error = self._uberftpls("/".join(location.split('/')[:-1]))
        if "No match " in error:
            raise Exception("file %s cannot be found: %s"%(location, error))
        result = result.split()
#        datetime =self._extract_date(result)
#        filename = result[-1]
        return result
#        return {'location':location, 'datetime':datetime, 'filename':filename, 'raw':result}

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
        locations = ['gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/archive',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sksp_natalie',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/LGPPP',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/PiLL',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/test',
                     'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/NDPPP'
#                     'gsiftp://gridftp.grid.sara.n:2811l/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/DISC'
                     ]
        if self.parent_dir in locations:
            raise Exception("FORBIDDEN to delete this {} because its parent is {}".format(
                            'file' if self.is_file else 'folder', self.parent_dir))

    def delete(self):
        parent_dir = self.get_parent_dir()
        self._donotdelete(parent_dir)
        if self.is_dir and not self.is_empty():
            raise Exception("Not allowed to delete a folder that isn't empty yet" )
        del_proc = Popen(['uberftp','-rm',self.location], stdout=PIPE, stderr=PIPE)
        res, err = del_proc.communicate()
        if not err:
            return
        else: 
            warnings.warn('Deleting failed: {}'.format(err))
    
    def get_parent_dir(self):
        location = "/".join([i for i in self.location.split('/') if i])
        parent_dir = "/".join(location.split('/')[:-1])
        return parent_dir

    def _get_num_files(self):
        """If self is folder, gets the number of files in it"""
        if self.is_file:
            return 1
        res, err = self._uberftpls(self.location)
        num_files = len([x for x in res.split('\r\n') if x])
        return num_files

    def _uberftpls(self, location):
        sub = Popen(['uberftp','-ls', location], stdout=PIPE, stderr=PIPE)
        res, err = sub.communicate()
        if err:
            warnings.warn("Uberftp -ls gave us an error for location {}: {}".format(location, err))
        return res, err

    def is_empty(self):
        if self._get_num_files() == 0:
            return True
        return False

    def list_dir(self):
        """Checks the status of all srm links in the folder given. 
        Returns a list of localities
        """     
        if self.is_dir:
           results, error= self._uberftpls(self.location)
        else: 
            return []
        if results == '':
            return []
        results = results.strip().split("\r\n")
        file_locs = [self.location +"/"+str(i.split()[-1])
                for i in results]
        files_list = [GSIFile(i,parent_dir=r) for i,r in zip(file_locs,results)]
        return files_list                                  
    
def get_srmdir_from_token_task(token_type, view, key = 'RESULTS_DIR'):
    pc=picas_cred()
    th=Token.Token_Handler(t_type=token_type, uname=pc.user, pwd=pc.password, dbn=pc.database)
    tokens=th.list_tokens_from_view(view)
    srmdir, OBSID = None, None
    for t in tokens: #TODO: Do this with a proper view
        if srmdir is not None: break
        OBSID = th.database[t['id']]['OBSID']
        if OBSID:
            srmdir_location = str(th.database[t['id']][key])+str(OBSID)
            srmdir = GSIFile(srmdir_location)
    return srmdir

def make_srmlist_from_srmdir(srmdir):
    slist = srmlist()
    for i in srmdir.list_dir():
        slist.append(i.location)


