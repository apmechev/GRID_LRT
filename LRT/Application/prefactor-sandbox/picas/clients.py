# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 11:40:06 2012

@author: Jan Bot
"""
# Python imports
import random

# CouchDB imports
import couchdb
from couchdb import Server

class CouchClient(object):
    """Client class to handle communication with the CouchDB back-end.
    """
    def __init__(self, url="http://localhost:5984", db="test",
            username="", password=""):
        """Create a CouchClient object. 
        :param url: the location where the CouchDB instance is located, 
        including the port at which it's listening. Default: http://localhost:5984
        :param db: the database to use. Default: test.
        """
        self.server = Server(url=url)
        if username == "":            
            self.db = self.server[db]
        else:
            self.db = couchdb.Database(url + "/" + db)
            self.db.resource.credentials = (username, password)
        
    def get_all(self, viewLoc, view_params={}):
        """
        .. function:: get_all(viewLoc[, view_params={}])
        :param viewLoc: location of the view in 'design/view' notation.
        :param view_params: optional extra parameters for the view.
        :return: row list returned by the view.
        """
        view = self.db.view(viewLoc)
        return view.rows
        
    def get_token(self, viewLoc, view_params={}, window_size=1):
        """Get a token from the specified view.
        :param view: the view to get the token from.
        :param view_params: the parameters that should be added to the view
        request. Optional.
        :param window_size: the size of the initial request to CouchDB, only
        one record within that set, which is randomly selected, is returned.
        :return: a CouchDB token.
        """
        view = self.db.view(viewLoc, limit=window_size, **view_params)
        l = len(view.rows)
        if l == 0:
            raise IndexError("None available.")
        i = random.randint(0, l-1)
        row = view.rows[i]
        return (row['key'], row['value'])
    
    def modify_token(self, token):
        """Modify a token.
        :param token: the token to be modified.
        :return: the modified token (including new _rev).
        """
        self.db[token['_id']] = token
        return token

    def update_all(self, rows):
        status = self.db.update(rows)
        return status
        
