
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






