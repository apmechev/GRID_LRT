import sys

if sys.version_info[0] < 3:
    from GRID_LRT.couchdb.util2 import *
else:
    from GRID_LRT.couchdb.util3 import *

def pyexec(code, gns, lns):
    # http://bugs.python.org/issue21591
    exec(code, gns, lns)
