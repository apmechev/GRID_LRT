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
* user account to the lofar ui at grid.surfsara.nl
* Login to the PiCaS client at picas-lofar.grid.sara.nl
* Active Grid certificate for launching jobs/accessing storage
* Astron LTA credentials for staging LOFAR data

Grid job submission and queuing
===============================

Data Staging
------------
In order to stage the data using the ASTRON LTA api, you need credentials to the [ASTRON LTA service](https://www.astron.nl/lofarwiki/doku.php?id=public:lta_howto#staging_data_prepare_for_download). These credentials need to be saved in a file on the lofar ui at ~/.stagingrc in the form 

user=uname
password=pswd


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
