'''
Toolbox for couchdb interaction tailored to the Grid

@copyright:  2016 SURFsara. All rights reserved.

@author:     Natalie Danezi

@license:    Apache 2.0

@contact:    helpdesk@surfsara.nl
'''

import credentials
import couchdb
from couchdb.design import ViewDefinition
import os
import re
import tempfile
import logging
import inspect
from time import time
from subprocess import Popen, PIPE


def connect_to_couchdb(url=credentials.URL, username=credentials.USERNAME,
                       password=credentials.PWD, dbname=credentials.DBNAME):
    """
    Connect to the database with the credentials set in "credentials.py" file.
    It returns a couchdb object (not truly connect) since couchdb is RESTFULL and no
    separate connection is made for authorization and authentication.
    """

    db = couchdb.Database(url + "/" + dbname)
    db.resource.credentials = (username, password)
    print("Connection established with: " + dbname)
    return db


def reset_locked_tokens(view_name=credentials.VIEW_NAME, hour=72):
    """
    Reset tokens that are locked for more time than hour (default=72) in the specified view (
    default=VIEW_NAME in credentials file).
    The function is used to release the lock of tokens that were killed when the job hit the queue
    limit (e.g 72 hours for the long queue).
    """
    db = connect_to_couchdb()

    max_age = time() - (hour * 3600)
    to_update = []
    for row in db.iterview(view_name + "/" + "locked", 100):
        doc = db[row["id"]]
        if (doc["lock"] < max_age):
            reset_doc_values(doc)
            to_update.append(doc)

    db.update(to_update)
    #print(to_update)
    print("Number of reset tokens in locked state: " + str(len(to_update)))


def reset_view_tokens(view_name=credentials.VIEW_NAME, state="error"):
    """
    Reset all the tokens in the specified view (default=VIEW_NAME in credentials file) in a
    particular state (default="error").
    """
    db = connect_to_couchdb()

    to_update = []
    for row in db.iterview(view_name + "/" + state, 100):
        doc = db[row["id"]]
        reset_doc_values(doc)
        to_update.append(doc)

    db.update(to_update)
    # print(to_update)
    print("Number of reset tokens in " + state + " state: " + str(len(to_update)))


def reset_doc_values(doc):
    """
    Reset the values of a token to make it available in the todo list and increase the
    scrub_count to account the amount of fails.
    This function returns the document but does not save the changes in the database.
    """

    doc['lock'] = 0
    doc["done"] = 0
    doc["scrub_count"] += 1
    doc['hostname'] = ''
    doc['exit_code'] = ''

    #uncomment to delete all attachments if present
    """
    if doc.has_key("_attachments"):
        del doc["_attachments"]
    """

    #add here any other application-specific values to reset


def delete_view_tokens(view_name=credentials.VIEW_NAME, state="todo"):
    """
    Delete all the tokens in the specified view (default=VIEW_NAME in credentials file) in a
    particular state (default="todo").
    """
    db = connect_to_couchdb()

    to_delete = []
    for row in db.iterview(view_name + "/" + state, 100):
        doc = db[row["id"]]
        to_delete.append(doc)
        db.delete(doc)

    #print(to_delete)
    print("Number of deleted tokens in " + state + " state: " + str(len(to_delete)))


def create_view_states(view_name=credentials.VIEW_NAME):
    """
    Create basic states (todo, lock, error, done, overview) in the specified view (
    default=VIEW_NAME in credentials file).
    Assumption: the view_name determines the token_type.
    """

    db = connect_to_couchdb()

    generalViewCode = '''
    function(doc) {
       if(doc.type == "%s") {
        if(%s) {
          emit(doc._id, doc._id);
        }
      }
    }
    '''

    #todo view
    todoCondition = 'doc.lock == 0 && doc.done == 0'
    todo_view = ViewDefinition(view_name, 'todo', generalViewCode %(view_name,todoCondition))
    todo_view.sync(db)

    #locked view
    lockedCondition = 'doc.lock > 0 && doc.done == 0'
    locked_view = ViewDefinition(view_name, 'locked', generalViewCode %(view_name,lockedCondition))
    locked_view.sync(db)

    #done view
    doneCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0'
    done_view = ViewDefinition(view_name, 'done', generalViewCode %(view_name,doneCondition))
    done_view.sync(db)

    #error View
    errorCondition = 'doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0'
    error_view = ViewDefinition(view_name, 'error', generalViewCode %(view_name,errorCondition))
    error_view.sync(db)

    #overview view
    overviewMapCode = '''
    function(doc) {
       if(doc.type == "%s") {
           if (doc.lock == 0 && doc.done == 0){
              emit('todo', 1);
           }
           if(doc.lock > 0 && doc.done == 0) {
              emit('locked', 1);
           }
           if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) == 0) {
              emit('done', 1);
           }
           if(doc.lock > 0 && doc.done > 0 && parseInt(doc.exit_code) != 0) {
              emit('error', 1);
           }
       }
    }
    '''
    overviewReduceCode='''
    function(key, values, rereduce)
    {
    return sum(values);
    }
    '''
    overview_total_view = ViewDefinition(view_name, 'overview', overviewMapCode %(view_name),
                                         overviewReduceCode)
    overview_total_view.sync(db)

    print(view_name + " view states created: todo, locked, done, error, overview")



def create_tokens(token_type=credentials.VIEW_NAME):
    """
    Create new tokens of a certain token_type (default=VIEW_NAME in credentials file).
    Assumption: the view_name determines the token_type.
    """

    db = connect_to_couchdb()

    tokens = []
    i = 0
    #create for example 50 tokens
    for i in range(50):
        token = {
            '_id': token_type + '_token_' + str(i),
            'type': token_type,
            'lock': 0,
            'done': 0,
            'scrub_count': 0,
            'hostname': '',
            'exit_code': ''
            # add here any other application-specific attributes for the token
        }
        tokens.append(token)
        i = i +1
    db.update(tokens)

    print("Number of " + token_type + " tokens created: " + str(len(tokens)))


if __name__ == '__main__':
    pass
