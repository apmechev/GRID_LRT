# This is the Stager API wrapper module for the Lofar LTA staging service.
#
# It uses an xmlrpc proxy to talk and authenticate to the remote service. Your account credentials will be read from
# the awlofar catalog Environment.cfg, if present or can be provided in a .stagingrc file in your home directory. 
#
# !! Please do not talk directly to the xmlrpc interface, but use this module to access the provided functionality. 
# !! This is to ensure that when we change the remote interface, your scripts don't break and you will only have to 
# !! upgrade this module.

__version__ = "1.0"

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib
import datetime
from os.path import expanduser
import pdb

#---
# Determine credentials and create proxy
user = None
passw = None
try:
    with open(expanduser("~/.awe/Environment.cfg"),'r') as file:
        print(datetime.datetime.now(), "stager_access: Parsing user credentials from", expanduser("~/.awe/Environment.cfg"))
        for line in file:
            if line.startswith("database_user"):
                user = line.split(':')[1].strip()
            if line.startswith("database_password"):
                passw = line.split(':')[1].strip()
except IOError:
    try:
        with open(expanduser("~/.stagingrc"),'r') as file:
            print(datetime.datetime.now(), "stager_access: Parsing user credentials from", expanduser("~/.stagingrc"))
            for line in file:
                if line.startswith("user"):
                    user = line.split('=')[1].strip()
                if line.startswith("password"):
                    passw = line.split('=')[1].strip()
    except IOError:
        print("No StagingRC file found")

if user and passw:
    print(datetime.datetime.now(), "stager_access: Creating proxy")
    proxy = xmlrpclib.ServerProxy("https://"+user+':'+passw+"@webportal.astron.nl/service-public/xmlrpc")
else:
    print("No User or Password exist. ")
# ---

class HandleXMLRPCException(object):
    """ Decorator class for all stager_access functions that catches the exception
    thrown by xmlrpc and replaces the password with [REDACTED]
    """
    func = None
    def __init__(self, replacement="[REDACTED]"):
        self.replacement = replacement

    def __call__(self, *args, **kwargs):
        if self.func is None:
            self.func = args[0]
            return self
        try:
            return self.func(*args, **kwargs)
        except xmlrpclib.ProtocolError as err:
            pdb.set_trace()
            if passw in err.url:
                err.url=err.url.replace(passw,self.replacement)
            raise(err)

@HandleXMLRPCException()
def stage(surls):
    """ Stage list of SURLs """
    if isinstance(surls, str):
        surls = [surls]
    stageid = proxy.LtaStager.add_getid(surls)
    return stageid

@HandleXMLRPCException()
def get_status(stageid):
    """ Get status of request with given ID """
    return proxy.LtaStager.getstatus(stageid)

@HandleXMLRPCException()
def abort(stageid):
    """ Abort running request / release data of a finished request with given ID """
    return proxy.LtaStager.abort(stageid)

@HandleXMLRPCException()
def get_surls_online(stageid):
    """ Get a list of all files that are already online for a running request with given ID  """
    return proxy.LtaStager.getstagedurls(stageid)

@HandleXMLRPCException()
def get_srm_token(stageid):
    """ Get the SRM request token for direct interaction with the SRM site via Grid/SRM tools """
    return proxy.LtaStager.gettoken(stageid)

@HandleXMLRPCException()
def reschedule(stageid):
    """ Reschedule a request with a given ID, e.g. after it was put on hold due to maintenance """
    return proxy.LtaStager.reschedule(stageid)

@HandleXMLRPCException()
def get_progress():
    """ Get a detailed list of all running requests and their current progress. As a normal user, this only returns your own requests.  """
    return proxy.LtaStager.getprogress()


@HandleXMLRPCException()
def get_storage_info():
    """ Get storage information of the different LTA sites, e.g. to check available disk pool space. Requires support role permissions. """
    return proxy.LtaStager.getsrmstorageinfo()

def prettyprint(dictionary, indent=""):
    """ Prints nested dict responses nicely. Example: 'stager_access.prettyprint(stager_access.get_progress())'"""
    if type(dictionary) is dict:
        for key in sorted(dictionary.keys()):
           item = dictionary.get(key)
           if type(item) is dict:
              print(indent+'+ ' +str(key))
              prettyprint(item, indent=indent+'  ')
           else:
              print(indent+'- '+str(key),'\t -> \t',str(item))
    else:
	    print("stager_access: This prettyprint takes a dict only!")

