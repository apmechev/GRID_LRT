# -*- coding: utf-8 -*-
"""
Created on Mon Jun  4 11:46:25 2012

@author: Jan Bot
"""

import sys
import time

class RunActor(object):
    """Executor class to be overwritten in the client implementation.
    """
    def __init__(self, iterator, modifier):
        """
        @param iterator: the view iterator to get the tokens from.
        """
        self.iterator = iterator
        self.client = iterator.client
        self.modifier = modifier
    
    def run(self, maxtime=-1):
        """Run method of the actor, executes the application code by iterating
        over the available tokens in CouchDB.
        """
        start = time.time()
        self.prepare_env()
        for key, ref, token in self.iterator:            
            self.prepare_run()
            self.process_token(ref, token)
            self.cleanup_run()
            if maxtime > 0:
                now = time.time()
                if now - start > maxtime:
                    sys.exit(0)
        self.cleanup_env()
        
    def prepare_env(self, *kargs, **kwargs):
        """Method to be called to prepare the environment to run the 
        application.
        """
        pass
    
    def prepare_run(self, *kargs, **kwargs):
        """Code to run before a token gets processed. Used e.g. for fetching
        inputs.
        """
        pass
    
    def process_token(self, key, token):
        """The function to overwrite which processes the tokens themselves.
        @param key: the token key. Should not be used to hold anything
        informative as it is mainly used to determine the order in which the
        tokens are returned.
        @param key: the key indicating where the token is stored in the 
        database.
        @param token: the token itself. !WARNING
        """
        modification = ()
        for k, v in token.iteritems():
            print k, v
        raise NotImplementedError
        return modification

    def cleanup_run(self, *kargs, **kwargs):
        """Code to run after a token has been processed.
        """
        pass
    
    def cleanup_env(self, *kargs, **kwargs):
        """Method which gets called after the run method has completed.
        """
        pass
    
    def unlock_all(self, view):
        rows = self.client.get_all(view)
        updated_tokens = []
        for row in rows:
            updated_tokens.append(
                    self.modifier.unlock(row['key'], row['value'])
            )
        status = self.client.update_all(updated_tokens)
        return status
