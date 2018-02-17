from subprocess import Popen,PIPE

def GRID_credentials_enabled():
    if not check_uberftp():
        return False
    p=Popen(['uberftp','-ls','gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox'],stdout=PIPE, stderr=PIPE)
    res=p.communicate()
    if 'Failed to acquire credentials.'in res[1]:
        raise Exception("Grid Credentials expired! Run 'startGridSession lofar:/lofar/user/sksp' in the shell")
    return True

def check_uberftp():
    p=Popen(['which', 'uberftp'],stdout=PIPE,stderr=PIPE)
    o=p.communicate()
    if o[0]=='' and o[1]=='':
        return False
    return True
