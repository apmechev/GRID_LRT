# -*- coding: utf-8 -*-
"""
Created on Mon May 21 16:15:25 2012

@author: Jan Bot
"""

# Python imports
import random

# CouchDB immports
from couchdb import ResourceConflict

class ViewIterator(object):
    """Dummy class to show what to implement for a PICaS iterator.
    """
    def __init__(self, client, view, token_modifier, view_params={}):
        pass
    
    def __repr__(self):
        return "<ViewIterator object>"
    
    def __str__(self):
        return "<view: " + self.view + ">"
    
    def __iter__(self):
        """Python needs this."""
        return self
    
    def next(self):
        try:
            return self.claim_token()
        except IndexError:
            raise StopIteration
        raise StopIteration

class BasicViewIterator(ViewIterator):
    """Iterator object to fetch tokens while available.
    """
    def __init__(self, client, view, token_modifier, view_params={}):
        """
        @param client: CouchClient for handling the connection to the CouchDB
        server.
        @param view: CouchDB view from which to fetch the token.
        @param token_modifier: instance of a TokenModifier.
        @param view_params: parameters which need to be passed on to the view
        (optional).
        """
        self.client = client
        self.view = view
        self.token_modifier = token_modifier
        self.view_params = view_params
    
    def claim_token(self, allowed_failures=10):
        """Get the first available token from a view.
         @param allowed_failures: the number of times a lock failure may
         occur before giving up. Default=10.
        """
        count = 0
        while count < allowed_failures:
            count += 1
            try:
                (key, ref) = self.client.get_token(self.view, 
                        view_params=self.view_params, window_size=100)
                document_index = ref
                if type(ref) == list:
                    document_index = ref[0]
                record = self.client.db[document_index]
                modified_record = self.token_modifier.lock(record)
                return (key, ref, self.client.modify_token(modified_record) )
            except ResourceConflict:
                pass
        if count == allowed_failures:
            raise EnvironmentError("Unable to claim token.")


class MultiKeyViewIterator(ViewIterator):
    def __init__(self, client, view, modifier, key_iterator, view_params={}):
        self.client = client
        self.view = view
        self.token_modifier = modifier
        self.key_iterator = key_iterator
        self.view_params = view_params
        self.get_view_keys()
        self.view_params.update(self.keys)
    
    def get_view_keys(self):
        try:
            self.keys = self.key_iterator.next()
            print self.keys
        except:
            raise StopIteration
    
    def claim_token(self, allowed_failures=10):
        count = 0
        while count < allowed_failures:
            try:
                (key, ref) = self.client.get_token(self.view, 
                        self.view_params)
                record = ref
                if type(ref) == list:
                    document_index = ref[0]
                    record = self.client.db[document_index]
                modified_token = self.token_modifier.lock(record)
                return (key, self.client.modify_token(modified_token) )
            except ResourceConflict:
                pass
            except IndexError:
                self.get_view_keys()
                self.view_params.update(self.keys)


class ViewKeyIterator(object):
    def __init__(self, values, perms):
        self.values = values
        self.perms = perms
    
    def __iter__(self):
        return self
    
    def next(self):
        if len(self.values) > 0:
            value = self.values.pop(random.randint(0, len(self.values)-1 ) )
            return {
                "startkey":[value, 0],
                "endkey": [value, self.perms]
            }
        else:
            raise StopIteration
