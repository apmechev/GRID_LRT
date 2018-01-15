#!/usr/bin/env python 
"""Module to read and store PiCaS credentials

"""
import datetime
from os.path import expanduser,isfile
from os import environ, chmod
import logging 

__author__ = "Alexandar Mechev"
__credits__ = ["Alexandar Mechev", "Natalie Danezi", "Timothy Shimwell", 
                "Raymond Oonk"]
__license__ = "GPL 3.0"
__version__ = "0.1.1"
__maintainer__ = "Alexandar Mechev"
__email__ = "apmechev@strw.leidenuniv.nl"
__status__ = "Production"

def infolog(string):
    if not logging:
        print("INFO: "+string)
    else:
        logging.info(string)

def debuglog(string):
    if not logging:
        print("DEBUG: "+string)
    else:
        logging.debug(string)

def warnlog(string):
    if not logging:
        print("WARNING: "+string)
    else:
        logging.warn(string)


class picas_cred(object):
    """Getting PiCaS credentials from environment or .picasrc file

    This class stores the picas credential in internal variables:
        user: PiCaS username
        password: PiCaS password
        database: (default) PiCaS database
    
    The ~/.picasrc file is in the following format:

user=picas_username
password=picas_password
database=picas_database

    """

    def __init__(self,source_file=None,usr=None,pwd=None,dbn=None):
        """ picas_creds gets credentials either automatically or manually
        
        If custom variables file exists, credentials are taken from source_file
        default source file is ~/.picasrc, gets from there if file exists
        If no ~/.picasrc, the credentials are from environment
        Finally, credentials can be put in the constructor

        Args:
            source_file (str): the location of file storing PiCaS credentials
            usr (str): picas user with which to initialize class
            pwd (str): picas password for above user
            dbn (str): picas database
        """
        if source_file:
            self.get_picas_creds_from_file(pic_file=source_file) 
        elif usr==None or pwd==None and dbn!=None:
                if isfile(expanduser('~/.picasrc')):
                    self.get_picas_creds_from_file('~/.picasrc')
                else:
                    self.get_picas_creds_from_env()
        else:
            self.user=usr
            self.password=pwd
            self.database=dbn


    def get_picas_creds_from_file(self,pic_file='~/.picasrc'):
        """ loads picas credentials from a file (default: ~/.picasrc)

            Args:
                pic_file(str): file from which to load the credentials 
                               (default: ~/.picasrc)
        """
        with open(expanduser(pic_file),'r') as file:
            infolog(str("picas_credentials: Parsing user credentials from "+str(expanduser(pic_file)))) 
            for line in file:
                if line.startswith("user"):
                    self.user = line.split('=')[1].strip()
                if line.startswith("password"):
                    self.password = line.split('=')[1].strip()
                if line.startswith("database"):
                    self.database = line.split('=')[1].strip()
    
    def get_picas_creds_from_env(self):
        """ Loads the PiCaS credentials from the environment

            The username, password and database must be stored
            in the variables $PICAS_USR, $PICAS_USR_PWD and $PICAS_DB

        """
        try:
            self.user=environ['PICAS_USR']
            self.password=environ['PICAS_USR_PWD']
            self.database=environ['PICAS_DB']
        except KeyError:
            warnlog("PICAS Variable not in ENV!") 
   
    def get_picas_creds(self):
        """ Automatically gets the PiCaS credentials

            Note:
                This function preferably gets the variables from environment
        """
        if not environ.get('PICAS_USR') and not environ.get('PICAS_USR_PWD') and not environ.get('PICAS_DB'):
            return self.get_picas_creds_from_env()
        else:
            return self.get_picas_creds_from_file()
    
    def put_picas_creds_in_env(self,picas_db=None):
        """ Inserts PiCaS credentials in environment

        This method is useful if scripts in this shell and subshells
        require the variables to be inside the environment.

        Args:
            picas_db (str): User can set a custom database, by default, 
                            the one from the class is used 
        """
        if picas_db:
            self.database=picas_db
            creds['PICAS_DB']=picas_db
        environ['PICAS_USR']=self.user
        environ['PICAS_USR_PWD']=self.password
        if self.database:
            environ['PICAS_DB']=self.database
        else: environ['PICAS_DB']=self.database
        return #self.get_picas_creds()

    def put_creds_in_file(self,pic_file="~/.picasrc"):
        """Exports PiCaS variables into a file

        Args:
            pic_file(str): File to write the variables in (default: ~/.picasrc)
        """
        with open(expanduser(pic_file),'w') as file:
            file.write("user="+str(self.user)+"\n")
            file.write("password="+str(self.password)+"\n")
            file.write("database="+str(self.database)+"\n")
        chmod(expanduser(pic_file),384)

    def return_credentials(self):
        """ Returns a dictionary of PiCaS credentials.

            d=pcred.return_credentials
            d.keys()=['user','password','database']
        """
        return {'user':self.user, 'password':self.password,'database':self.database}


if __name__ == '__main__':    #code to execute if called from command-line
    infolog("PiCaS_creds from main()")
    if isfile(expanduser('~/.picasrc')):
        pc=picas_cred(source_file='~/.picasrc')
        pc.put_picas_creds_in_env()
    else:
        pc=picas_cred()
        pc.put_creds_in_file()        
