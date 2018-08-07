[![Documentation Status](https://readthedocs.org/projects/grid-lrt/badge/?version=latest)](http://grid-lrt.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/apmechev/GRID_LRT.svg?branch=master)](https://travis-ci.org/apmechev/GRID_LRT)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/GRID-LRT.svg)](https://badge.fury.io/py/GRID-LRT)
[![alt text](http://apmechev.com/img/git_repos/GRID_LRT_clones.svg "github clones since 2017-01-25")](https://github.com/apmechev/github_clones_badge)
[![codecov Coverage](https://codecov.io/gh/apmechev/GRID_LRT/branch/master/graph/badge.svg?precision=1)](https://codecov.io/gh/apmechev/GRID_LRT)
[![alt text](http://apmechev.com/img/git_repos/pylint/GRID_LRT.svg "pylint score")](https://github.com/apmechev/pylint-badge)
[![BCH compliance](https://bettercodehub.com/edge/badge/apmechev/GRID_LRT?branch=master)](https://bettercodehub.com/)
[![DOI](https://zenodo.org/badge/53421495.svg)](https://zenodo.org/badge/latestdoi/53421495)

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

Installing with pip
---------

The GRID LOFAR Reduction Tools are now available through pip:

```bash
pip install GRID_LRT

```

Manual build
------
Alternatively you should use the setup.py script to install the tools:

```
python setup.py build
python setup.py install
```

If you do not have permissions to write to the default Python package directory, you can use

```
python setup.py install --perfix={PATH_WHERE_TO_INSTALL_PACKAGE}
```

You have to make sure that this path 1. Exists, 2. Is in your PYTHONPATH and 3. Will be in your PYTHONPATH every time you enter your shell (add it to your ~/.bashrc)



Tutorial Notebook
==============

Best way to get acquainted with the software is with the tutorial notebook available at GRID\_LRT/tutorials/LRT\_demo.ipynb

Setting up Jupyter on loui
----------------

```bash
$> ssh loui.grid.sara.nl
[10:42 me@loui ~] > mkdir ~/.jupyter
[10:42 me@loui ~] > export PATH=/cvmfs/softdrive.nl/anatolid/anaconda-2-2.4.0/bin:$PATH
[10:42 me@loui ~] > export LD_LIBRARY_PATH=/cvmfs/softdrive.nl/anatolid/anaconda-2-2.4.0/lib:$LD_LIBRARY_PATH
[10:42 me@loui ~] > jupyter notebook password


```

Running a Jupyter notebook on loui
---------------
Assuming you have ssh login to loui, you can run this notebook on your own machine by using ssh port forwarding : 

```bash
$> ssh -L 8888:localhost:8888 loui.grid.sara.nl
[10:42 me@loui ~] > source /home/apmechev/.init_jupyter
```

With that shell running, you can open the browser on your local machine and go to localhost:8888, and browse to the tutorials folder. 


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
from GRID_LRT.Staging import stager_access 
stageID=stage_all_LTA.main('srm.txt') #Here is the path to your srm_file.
print(stageID) # the stageID is your identifier to the staging system. You can poll it with:
print(stage_all_LTA.get_stage_status(stageID)) # prints out a 'status' string

statuses=stager_access.get_progress()
print(statuses[stageID]) # More detailed information on your staging request
```

Because of design choices at the Astron service, when your staging is complete, the last 2 commands above will fail! The get\_stage\_status function appears to return 'success' though.

Creating a Sandbox
--------------------

In order to make processing portable, all scripts are archived in a 'sandbox', which is extracted to an empty temporary folder on the worker node. This architecture choice also makes it easy to test a clean environment on the login node or even your laptop. 



PiCaS Tokens
--------------------

Job 'Tokens' are a way to define your jobs.  


[Mooc](http://docs.surfsaralabs.nl/projects/grid/en/latest/Pages/Tutorials/MOOC/mooc.html#mooc-picas-client)

[Utility](https://ganglia.surfsara.nl/?r=hour&cs=&ce=&c=GINA+Servers&h=&tab=ch&vn=&hide-hf=false&m=load_one&sh=1&z=small&hc=4&host_regex=&max_graphs=0&s=by+name)

Node-side processing
====================

Now that the data is staged, jobs are defined, scripts are bundled and jobs submitted, here's what happens on the worker node:

Launching and Locking Tokens
--------------------------------


Intermediate Storage
=====================================


Other
=========================

---                                                                                                      
author:
- 'Alexandar P. Mechev, Raymond Oonk'
title: |
    GRID\_LRT: LOFAR Reduction Tools for The Dutch Grid\

    A set of tools to reduce LOFAR Data: infrastructue and usage 
... 


