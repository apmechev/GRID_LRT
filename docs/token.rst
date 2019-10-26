
Tokens
=================

The GRID_LRT.Token module is responsible for interactions with CouchDB using the PiCaS token framework. It contains a **Token_Handler** object which manages a single _design document on CouchDB, intended for a set of jobs that are logically linked together. In the LOFAR Surveys case, this holds the jobs of a single Observation. Additionally a **Token_Set** object can create batch tokens, upload attachments to them in bulk and change Token fields in bulk as well. This module is used in combination with the  :ref:`srmlist <srmlist-doc>` class to automatically create sets of jobs with N files each.

token.py
--------
Location: GRID_LRT/token.py

Imports:

>>> from GRID_LRT.token import Token, TokenBuilder #Abstract classes
>>> from GRID_LRT.token import caToken, TokenJsonBUilder, TokenList, TokenView
>>> from GRID_LRT.token import TokenSet

Usage: 

>>> #Example creation of a token of token_type 'test'
>>> from GRID_LRT.auth.get_picas_credentials import picas_cred
>>> pc=picas_cred() #Gets picas_credentials
>>>
>>> from cloudant.client import CouchDB         
>>> from GRID_LRT.token import caToken #Token that implements the cloudant interface
>>> from GRID_LRT.token import TokenList
>>> client = CouchDB(pc.user,pc.password, url='https://picas-lofar.grid.surfsara.nl:6984',connect=True)
>>> db = client[pc.database]
>>> 'token_id' in db # Checks if database includes the token
>>> db['token_id'] #Pulls the token 
>>> tl = TokenList(database=db, token_type='token_type') #makes an empty list
>>> tl.add_view(TokenView('temp',"doc.type == \"{}\" ".format(tl.token_type))) # adds a view to the token
>>> for token in tl.list_view_tokens('temp'):
        tl.append(caToken(token_type=tl.token_type, token_id= token['_id'], database=db))
# adds every token in view to the local list (only their ids)
>>> tl.fetch() #Fetch actual data for token in list
>>> t1 = caToken(database=db, token_type='restructure_test', token_id=token_id) #make a token (locally)
>>> t1.build(TokenJsonBuilder('/path/to/token/data.json'))
>>> t1.save() #upload to the database
>>> t1.add_attachment(attachment_name='attachment_name_in_db.txt',filename='/path/to/attachment/file') #Adds attachment to token


Tokens
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GRID_LRT.token.Token
    :members: 
    :undoc-members:

.. autoclass:: GRID_LRT.token.caToken
    :members:
    :undoc-members

TokenSet
~~~~~~~~~~~~~~~~~~~~~~

.. autoclass:: GRID_LRT.token.TokenSet
    :members: 
    :undoc-members:






