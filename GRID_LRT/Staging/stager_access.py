"""
It uses an xmlrpc proxy to talk and authenticate to the remote service.
Your account credentials will be read from the awlofar catalog Environment.cfg,
if present or can be provided in a .stagingrc file in your home directory.

!!Please do not talk directly to the xmlrpc interface,
but use this module to access the provided functionality.
!! This is to ensure that when we change the remote interface,
your scripts don't break and you will only have to upgrade this module.
"""
from __future__ import print_function
import os
from os.path import expanduser
import datetime
from functools import wraps

try:
    import xmlrpclib
except ImportError:
    import xmlrpc.client as xmlrpclib  # pylint: disable=import-error

__version__ = "1.0"

# ---
# Determine credentials and create proxy
USER = None
PASSW = None

def get_staging_creds():
    """Function to get the staging credentials first from
       ~/.awe/Environment.cfg, if not there, then from ~/.stagingrc
       and finally from the env variables LOFAR_LTA_USER and LOFAR_LTA_PWD
    """
    user = None
    passw = None
    try:
        with open(expanduser("~/.awe/Environment.cfg"), 'r') as authfile:
            print(datetime.datetime.now(), "stager_access: Parsing user credentials from",
                  expanduser("~/.awe/Environment.cfg"))
            for line in authfile:
                if line.startswith("database_user"):
                    user = line.split(':')[1].strip()
                if line.startswith("database_password"):
                    passw = line.split(':')[1].strip()
    except IOError:
        try:
            with open(expanduser("~/.stagingrc"), 'r') as authfile:
                print(datetime.datetime.now(
                ), "stager_access: Parsing user credentials from", expanduser("~/.stagingrc"))
                for line in authfile:
                    if line.startswith("user"):
                        user = line.split('=')[1].strip()
                    if line.startswith("password"):
                        passw = line.split('=')[1].strip()
        except IOError:
            print("No StagingRC file found")
            try:
                user = os.environ['LOFAR_LTA_USER']
                passw = os.environ['LOFAR_LTA_PWD']
            except KeyError:
                print("LOFAR LTA USER/PASSW not in environment!")
    if user and passw:
        print(datetime.datetime.now(), "stager_access: Creating proxy")
        lta_proxy = xmlrpclib.ServerProxy(
            "https://"+user+':'+passw+"@webportal.astron.nl/service-public/xmlrpc")
    else:
        print("No User or Password exist. ")
        return "", "", ""
    return user, passw, lta_proxy

USER, PASSW, LTA_PROXY = get_staging_creds()
# ---


def handle_xmlrpc_exception(fun):
    """ Exception handler that stops xmlrpclib.ProtocolError
    from printing out the username and password to the terminal

    """
    @wraps(fun)
    def wrapper(*args, **kwds):
        """Wrapper around the function that captures the exception
        and DOES NOT print out the password in plain text"""
        try:
            return fun(*args, **kwds)
        except xmlrpclib.ProtocolError as err:
            if PASSW in err.url:
                err.url = err.url.replace(PASSW, '[REDACTED]')
            raise err
    return wrapper


@handle_xmlrpc_exception
def stage(surls):
    """ Stage list of SURLs or a string holding a single SURL

    :param surls: Either a list of strings or a string holding a single surl to stage
    :type surls: either a list() or a str()
    :return: An integer which is used to refer to the stagig request when polling
    the API for a staging status
    """
    staged_surls = []
    if isinstance(surls, str):
        staged_surls = [surls]
    for i in surls:
        staged_surls.append(str(i))
    stageid = LTA_PROXY.LtaStager.add_getid(staged_surls)
    return stageid


@handle_xmlrpc_exception
def get_status(stageid):
    """ Get status of request with given ID

    Args:
        :param stageid: The id of the staging request which you want the status of
        :type stageid: int

    Returns:
        :status: A string describing the staging status: 'new', 'scheduled',
        'in progress' or 'success'
        """
    return LTA_PROXY.LtaStager.getstatus(stageid)


@handle_xmlrpc_exception
def abort(stageid):
    """ Abort running request / release data of a finished request with given ID """
    return LTA_PROXY.LtaStager.abort(stageid)


@handle_xmlrpc_exception
def get_surls_online(stageid):
    """ Get a list of all files that are already online for a running request with given ID  """
    return LTA_PROXY.LtaStager.getstagedurls(stageid)


@handle_xmlrpc_exception
def get_srm_token(stageid):
    """ Get the SRM request token for direct interaction with the SRM site via Grid/SRM tools """
    return LTA_PROXY.LtaStager.gettoken(stageid)


@handle_xmlrpc_exception
def reschedule(stageid):
    """ Reschedule a request with a given ID, e.g. after it was put on hold due to maintenance """
    return LTA_PROXY.LtaStager.reschedule(stageid)


@handle_xmlrpc_exception
def get_progress():
    """ Get a detailed list of all running requests and their current progress.
    As a normal user, this only returns your own requests.  """
    return LTA_PROXY.LtaStager.getprogress()


@handle_xmlrpc_exception
def get_storage_info():
    """ Get storage information of the different LTA sites,
    e.g. to check available disk pool space. Requires support role permissions. """
    return LTA_PROXY.LtaStager.getsrmstorageinfo()


def prettyprint(dictionary, indent=""):
    """ Prints nested dict responses nicely. Example:
    'stager_access.prettyprint(stager_access.get_progress())'"""
    if isinstance(dictionary, dict):
        for key in sorted(dictionary.keys()):
            item = dictionary.get(key)
            if isinstance(item, dict):
                print(indent+'+ ' + str(key))
                prettyprint(item, indent=indent+'  ')
            else:
                print(indent+'- '+str(key), '\t -> \t', str(item))
    else:
        print("stager_access: This prettyprint takes a dict only!")
