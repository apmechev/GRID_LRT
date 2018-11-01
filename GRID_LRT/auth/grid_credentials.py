"""Small module responsible for checking whether standard
Grid tools exist and whether the GRID credentials are
activated
"""
import subprocess
from functools import wraps


def check_uberftp():
    """Checks if the uberftp executable
    exists on the system. Returns True if it exists

    :returns: bool"""
    process = subprocess.Popen(['which', 'uberftp'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()
    if output[0] == '' and output[1] == '':
        return False
    return True

def grid_credentials_enabled():
    """Short function that checks whether
    the GRID credentials have been enabled or expired
    Returns True if they are currenctly active

    This requires uberftp!"""
    if not check_uberftp():
        return False
    process = subprocess.Popen([
        'uberftp', '-ls',
        'gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    res = process.communicate()
    if type(res[1])==bytes:
        error = res[1].decode('utf8')
    else:
        error = res[1]
    if "Failed to acquire credentials." in error:
        raise Exception("Grid Credentials expired! "
                        "Run 'startGridSession lofar:/lofar/user/sksp' in the shell")
    return True


def skip_grid_auth(func):
    def wrapped(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except :
            raise Warning("Not authorized GRID user but continuing anyways")
    return wrapped

