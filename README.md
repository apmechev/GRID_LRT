[![Documentation Status](https://readthedocs.org/projects/grid-lrt/badge/?version=latest)](http://grid-lrt.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/apmechev/GRID_LRT.svg?branch=master)](https://travis-ci.org/apmechev/GRID_LRT)
[![License: GPL v3](https://img.shields.io/badge/License-GPL%20v3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/GRID-LRT.svg)](https://badge.fury.io/py/GRID-LRT)
[![alt text](http://apmechev.com/img/git_repos/GRID_LRT_clones.svg "github clones since 2017-01-25")](https://github.com/apmechev/github_clones_badge)
[![codecov Coverage](https://codecov.io/gh/apmechev/GRID_LRT/branch/master/graph/badge.svg?precision=1)](https://codecov.io/gh/apmechev/GRID_LRT)
[![alt text](http://apmechev.com/img/git_repos/pylint/GRID_LRT.svg "pylint score")](https://github.com/apmechev/pylint-badge)
[![BCH compliance](https://bettercodehub.com/edge/badge/apmechev/GRID_LRT?branch=master)](https://bettercodehub.com/)
[![Updates](https://pyup.io/repos/github/apmechev/GRID_LRT/shield.svg)](https://pyup.io/repos/github/apmechev/GRID_LRT/)


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

The [up to date installation instructions are here.](https://grid-lrt.readthedocs.io/en/latest/installing.html)

Attribution
=============
[![DOI](https://zenodo.org/badge/53421495.svg)](https://zenodo.org/badge/latestdoi/53421495)
[![ArXiV](http://img.shields.io/badge/arXiv-1712.00312-orange.svg?style=flat)](https://arxiv.org/abs/1712.00312)

If you actively use GRID\_LRT, please cite this software as such below:
```
@misc{apmechev:2018,
      author       = {Alexandar P. Mechev} 
      title        = {apmechev/GRID_LRT: v0.4.0},
      month        = aug,
      year         = 2018,
      doi          = {10.5281/zenodo.1341127},
      url          = {https://doi.org/10.5281/zenodo.1341127}
    }
```

If you're using GRID processed data, also consider citing the paper below, outlining the procedure of running LOFAR data through a High Throughput Cluster:

```
@INPROCEEDINGS{mechev2017,
   author = {{Mechev}, A. and {Oonk}, J.~B.~R. and {Danezi}, A. and {Shimwell}, T.~W. and                             
{Schrijvers}, C. and {Intema}, H. and {Plaat}, A. and {Rottgering}, H.~J.~A.},
    title = "{An {A}utomated {S}calable {F}ramework for {D}istributing {R}adio {A}stronomy {P}rocessing {A}cross {C}lusters and {C}louds}",
booktitle = {Proceedings of the International Symposium on Grids and Clouds (ISGC) 2017, held 5-10 March, 2017 at Academia Sinica, Taipei, Taiwan (ISGC2017). Online at \url{https://pos.sissa.it/cgi-bin/reader/conf.cgi?confid=293}, id.2},
     year = 2017,
archivePrefix = "arXiv",
   eprint = {1712.00312},
 primaryClass = "astro-ph.IM",
    month = mar,
      eid = {2},
      doi = {10.22323/1.293.0002},
    pages = {2},
   adsurl = {\url{http://adsabs.harvard.edu/abs/2017isgc.confE...2M}},
  adsnote = {Provided by the SAO/NASA Astrophysics Data System}
}


```



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

