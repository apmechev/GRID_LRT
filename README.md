---
author:
- 'Alexandar P. Mechev, Raymond Oonk'
title: |
    GRID\_LRT LOFAR Reduction Tools for The Dutch Grid\
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
minimal user interaction. The SARA\_LRT software package deals with the
queuing and submission of jobs to the grid nodes, saving of finished
products to a storage node and includes a modified version of the
prefactor pipeline suited to run on a grid infrastructue with the option
to select how many subbands run per node.


Sandbox Creation
================



Grid job submission and queuing
===============================

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
