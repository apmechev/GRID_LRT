"""GRID_LRT: Grid LOFAR Tools"""
from subprocess import PIPE, Popen
import os
__all__ = ["Application", "Staging", 'sandbox', 'Token', 'couchdb', "couchdb.tests"]
__version__ = "0.4.0"
__author__ = "Alexandar P. Mechev"
__copyright__ = "2018 Alexandar P. Mechev"
__credits__ = ["Alexandar P. Mechev", "Natalie Danezi", "J.B.R. Oonk"]
__license__ = "GPL 3.0"
__maintainer__ = "Alexandar P. Mechev"
__email__ = "LOFAR@apmechev.com"
__status__ = "Production"
__date__ = "2018-07-27"



def get_git_hash():
    """Gets the git hash using git describe"""
    proc = Popen(["git", "describe"], stdout=PIPE)
    label = proc.communicate()[0].strip()
    g_hash = label
    githashfile = __file__.split('__init__')[0]+"__githash__"
    if os.path.exists(githashfile):
        with open(githashfile) as _file:
            file_hash = _file.read().encode('utf-8')
    else:
        file_hash = ""
    if not str(g_hash) in file_hash:
        with open(githashfile, 'w') as _file:
            _file.write(str(g_hash))
    return g_hash


__commit__ = get_git_hash()
