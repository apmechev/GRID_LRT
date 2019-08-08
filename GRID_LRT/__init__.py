"""GRID_LRT: Grid LOFAR Tools"""
import sys
import os
import socket
from subprocess import call, Popen, PIPE, STDOUT
if sys.version_info[0:2] != (2, 6):
    from subprocess import check_output


__all__ = ["storage", 'auth', "application", "Staging", 'token']
__version__ = "1.0.0rc1"
__author__ = "Alexandar P. Mechev"
__copyright__ = "2019 Alexandar P. Mechev"
__credits__ = ["Alexandar P. Mechev", "Natalie Danezi", "J.B.R. Oonk"]
__bibtex__ = """@misc{apmechev:2019,
      author       = {Alexandar P. Mechev} 
      title        = {apmechev/GRID_LRT: v0.5.1},
      month        = sep,
      year         = 2019,
      doi          = {10.5281/zenodo.1438833},
      url          = {https://doi.org/10.5281/zenodo.1438833}
    }"""
__license__ = "GPL 3.0"
__maintainer__ = "Alexandar P. Mechev"
__email__ = "LOFAR@apmechev.com"
__status__ = "Production"
__date__ = "2019-02-13"
