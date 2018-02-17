import subprocess

def check_uberftp():
    p=subprocess.Popen(['which', 'uberftp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    o=p.communicate()
    if o[0].decode() == '' and o[1].decode() =='':
        return False
    return True

def GRID_credentials_enabled():
    if check_uberftp()==False:
        return False
    p=subprocess.Popen(['uberftp','-ls','gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox'],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res=p.communicate()
    if 'Failed to acquire credentials.'in res[1]:
        raise Exception("Grid Credentials expired! Run 'startGridSession lofar:/lofar/user/sksp' in the shell")
    return True

