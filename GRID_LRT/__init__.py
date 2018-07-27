"""GRID_LRT: Grid LOFAR Tools"""
import subprocess
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
__date__ = "``2018-07-27"



def get_git_hash():
    label = subprocess.check_output(["git", "describe"]).strip()
    g_hash=label.split(__version__+'-')[1]
    import GRID_LRT
    githashfile = GRID_LRT.__file__.split('__init__')[0]+"__githash__"
    with open(githashfile) as _file:
        file_hash = _file.read()
    if not g_hash in file_hash:
        with open(githashfile,'w') as _file:
            _file.write(g_hash)
    return g_hash


__commit__ = get_git_hash()
