
Token Module
=================

This module is responsible for interactions with CouchDB using the PiCaS token framework. It contains a **Token_Handler** object which manages a single _design document on CouchDB, intended for a set of jobs that are logically linked together. In the LOFAR Surveys case, this holds the jobs of a single Observation. Additionally a **Token_Set** object can create batch tokens, upload attachments to them in bulk and change Token fields in bulk as well. This module is used in combination with the  :ref:`srmlist <srmlist-doc>` class to automatically create sets of jobs with N files each.

Token.py
==========
Location: GRID_LRT/Token.py
Imports:

``` 

>>> from GRID_LRT.Token import Token_Handler
>>> from GRID_LRT.Token import TokenSet

```

Class Documentation:
TokenHandler
------

.. autoclass:: GRID_LRT.Token.Token_Handler
    :members: 
    :undoc-members:

TokenSet
------

.. autoclass:: GRID_LRT.Token.TokenSet
    :members: 
    :undoc-members:






