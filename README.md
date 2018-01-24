---
author:
- 'Alexandar P. Mechev, Raymond Oonk'
title: |
    GRID\_LRT: LOFAR Reduction Tools for The Dutch Grid\

    A set of tools to reduce LOFAR Data: infrastructue and usage 
...

Due to the large computational requirements for LOFAR datasets,
processing bulk data on the grid is required. This manual will detail
the Dutch grid infrastructure, the submission process and the types of
users anticipated to use the LOFAR reduction tools.

Overview
========

SurfSARA is the Dutch locations of the CERN Computational Grid and its
facilities are available for general scientific computing. Because the
LOFAR telescope requires significant computational resources, the
reduction pipelines have been fitted to run on the Dutch Grid nodes with
minimal user interaction. The GRID\_LRT software package automates LOFAR data staging,
job description, Pre-Factor parallelization, job submission and management of intermediate data.

Requirements:
============
* User account to the lofar ui at grid.surfsara.nl
* Login to the PiCaS client at picas-lofar.grid.sara.nl
* Active Grid certificate for launching jobs/accessing storage
* Astron LTA credentials for staging LOFAR data


Installing:
============
To use the package, it is recommended to install it using the setup.py script: 

```
python setup.py build

python setup.py install
```

If you do not have permissions to write to the default Python package directory, you can use

```
python setup.py install --perfix={PATH_WHERE_TO_INSTALL_PACKAGE}
```

You have to make sure that this path 1. Exists, 2. Is in your PYTHONPATH and 3. Will be in your PYTHONPATH every time you enter your shell (add it to your ~/.bashrc)

Grid job submission and queuing
===============================

Data Staging
------------
In order to stage the data using the ASTRON LTA api, you need credentials to the [ASTRON LTA service](https://www.astron.nl/lofarwiki/doku.php?id=public:lta_howto#staging_data_prepare_for_download). These credentials need to be saved in a file on the lofar ui at ~/.stagingrc in the form 

```
user=uname

password=pswd
```

Staging requires a list of srms to be staged (typically srm.txt)

It can be done with this set of commands:

```python 
from GRID_LRT.Staging import stage_all_LTA

stageID=stage_all_LTA.main('srm.txt') #Here is the path to your srm_file.

print(stageID) # the stageID is your identifier to the staging system. You can poll it with:


print(stage_all_LTA.get_stage_status(stageID)) # prints out a 'status' string

statuses=stager_access.get_progress()

print(statuses[stageID]) # More detailed information on your staging request
```

Because of design choices at the Astron service, when your staging is complete, the last 2 commands above will fail! The get\_stage\_status function appears to return 'success' though.

[Mooc](http://docs.surfsaralabs.nl/projects/grid/en/latest/Pages/Tutorials/MOOC/mooc.html#mooc-picas-client)

[Utility](https://ganglia.surfsara.nl/?r=hour&cs=&ce=&c=GINA+Servers&h=&tab=ch&vn=&hide-hf=false&m=load_one&sh=1&z=small&hc=4&host_regex=&max_graphs=0&s=by+name)

Node-side processing
====================

NDPPP Parset Execution fad\_LRT.py
----------------------------------

Custom Script Execution fad\_LRT.py
-----------------------------------


GRID Prefactor prefactor\_LRT.py
--------------------------------


Surls, Staging and Storage of results
=====================================

LRT Architecture
================
