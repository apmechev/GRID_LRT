---
author:
- 'Alexandar P. Mechev, Raymond Oonk'
title: |
    SARA\_LRT LOFAR Reduction Tools for The Dutch Grid\
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

Grid job submission and queuing
===============================

[Mooc](http://docs.surfsaralabs.nl/projects/grid/en/latest/Pages/Tutorials/MOOC/mooc.html#mooc-picas-client)

Jobs to be launched on a grid node are containerized in a token, with
each token holding a job for one node. The token is the interface
between the user and the grid job, both used to send parameters to the
job and to upload logs and files by the job itself. Tokens are held in a
PiCaS database, which can be accessed through a python interface or
through the web. The token parameters include time and frequency steps
for averaging and demixing as well as switches which guide the job
execution on the node. Additionally, a custom parset can be passed as a
token parameter. Finally, the OBSID, srm hyperlink to the file and
subband number are written to the token.

While uploading tokens to the picasDB only requires a PiCaS account,
launching jobs requires a full grid certificate. The parameters of the
job are stored in a .jdl file and include the number of cores requested,
the number of jobs to launch, the PiCaS database from which to fetch
tokens and most importantly the sandbox which will be uploaded to the
job node. The sandbox contains *all* the files that will be sent to the
grid node, which is why often tarfiles are sent and then extracted once
the job launches. One final parameter to the grid job is the executable
to launch upon landing on a node. It pulls a token from the grid node
and parses its arguments, sending them to the main executable of the
sandbox.

When tokens are submitted but not running, they’re in the Todo state:
They’re waiting to be pulled by a grid node and executed. Once the
execution starts, the tokens are set as Locked, meaning they’re
executing. When they complete with an exit status of 0, they’re set to
Done, otherwise they’re set as Error and the return value is displayed
in the token. Additionally the stdout and stderr logs are uploaded to
the database so the user can debug the jobs post-mortem.

In the case of a successful completion, the results are uploaded to a
storage node where they can be downloaded using globus-url-copy by a
user with a grid certificate or by another job.

Folder structure
================

The LRT folder structure compartmentalizes the different steps of the
job submission process which allows for running single steps and
checking the output. The folders include Application, Tokens and Staging
as well as gsurl and parsets.

The Application folder holds the job submission scripts as well as the
sandboxes which are sent to the node. As of LRT version 1.5, because of
limitations related to the token fetching mechanism, sandboxes
associated with an OBSID and Picas Username are uploaded to the grid
storage and pulled once the job starts. This allows different LOFAR
Tools to run concurrently as well as different steps of Prefactor to run
for different OBSIDS and the same user. The modification of the LRT
sandboxes is done by the launch scripts.

The Staging folder holds information about the srms of each OBSID/SB
combination, as well as the scripts to both check their storage state
and stage them. These scripts can handle files located on SARA, Juleich
and Poznan based on the path to the filename. In the dataset subfolder,
each OBSID holds a list of srms and subbands as well as the setup.cfg
file which passes parameters to the PiCaS token.

The Token folder contains the scripts for creating, deleting tokens as
well as creating views which fetch tokens that match specific
prerequisites. Tokens are a container of a physical job which hold the
status, start time, end time and parameters of the job. When they are
fetched on a node, the status of the token is set to locked, which
indicates the job is running on a node. Furthermore, the node name is
logged which allows the user to search for and monitor the activity on
it using this utility:

[Utility](https://ganglia.surfsara.nl/?r=hour&cs=&ce=&c=GINA+Servers&h=&tab=ch&vn=&hide-hf=false&m=load_one&sh=1&z=small&hc=4&host_regex=&max_graphs=0&s=by+name)

Node-side processing
====================

Once the job launches on a worker node, it downloads extracts the
appropriate sandbox and executes the pilot script. The pilot script
scrapes the tokens for parameters and passes them to the main execution
script. After the main script finishes, the pilot script attaches the
output to the couchDB token which is uploaded for the user to read.
Finally, the token’s status is set as Done or Error based on the output
of the main script.

The main script is responsible for the setup of the environment,
downloading of data, parsing of Observation ID, Subband and parameters,
execution of processing, and cleanup and uploading of results.

NDPPP Parset Execution fad\_LRT.py
----------------------------------

One of the facilites provided by the Lofar Reduction Tools is the
ability to quickly reduce large amounts of data with each subband on a
different node. The default mode of this mode allows the user to perform
the default RFI flagging strategy, and average a subband in time and
frequency. The user has the choice of averaging steps, whether to turn
on demixing on or off as well as the demix sources and an option to only
use Dutch stations. All those options are stored in a default.cfg file
which is an input to the fad\_LRT.py script as well as the srm file
listing which obsids/subbands the actions will be performed.

Additionally, the user may provide a custom parset, which is placed in
the FAD\_v1/parsets directory. In this case, the parset name is placed
in the custom.cfg file which is passed to fad\_LRT.py. This mode will be
made more frictionless in the next version by scrapping the .cfg file
and allowing the user to directly add a parset from commandline. Using a
custom parset, the rest of the .cfg options are ignored and the parset
is passed directly to NDPPP once the job launches on the node (After the
msin and msout are replaced with the appropriate filenames).

In earlier versions of the processing scripts, NDPPP would crash when
landing on a node with little memory. In order to minimize this, the
fad\_LRT.py scripts will split the input MS in chunks such that each MS
is less than 1/3 of free memory on the node, run them in sequence and
concatinate the results. This mode is turned on by default but can be
turned off using the -noTS or –no-time-splitting flags after
fad\_LRT.py.

Custom Script Execution fad\_LRT.py
-----------------------------------

The fad\_LRT.py script may also bypass the default/custom NDPPP
execution and launch a custom script on the worker node. The user may
pass their own script using python fad\_LRT.py -s script.py which is
sent to the worker node and executed in place of the vanilla NDPPP
execution.

Uploading results 
------------------

In the case that fad\_LRT completes successfully on the worker node, it
uploads its resulting MS.tar.gz onto the worker node in the folder

srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/\${OBSID}\_\${sbn}

GRID Prefactor prefactor\_LRT.py
--------------------------------

Aside from launching custom scripts and NDPPP parsets, the GRID LRT
package can launch prefactor with minimal modification and setup. If the
repository is cloned with git clone –recursive, the entire grid
prefactor pipeline will be added to a sandbox in the Application folder.

The difference of this branch from vanilla prefactor is minimal and
consists of two download scripts that walk through the srms requested
and download them on the node. Alternatively if no files exist in
Application/prefactor-sandbox/prefactor, the prefactor\_LRT.py script
will execute ’git submodule init’ and ’git submodule update’ which will
checkout the newest version of this repo in the appropriate folder.

Because the GRID infrastructure at the SurfSARA site doesn’t have a
shared filesystem, each node will execute work as a standalone machine.
This enforces embarassingly parallel work splitting, meaning that there
will be no inter-communication between nodes. In order to adapt
prefactor for this architecture, two download scripts were added to
prefactor that preceed the data processing. The first script,
getfiles.sh downloads and unters one subband as passed by an argument by
creating a FIFO pipe between the download and untarring steps. The
second script, download\_num\_files.sh, executes getfiles.sh for the
range of srms specified by two inputs and logs the process name.
Finally, the main script downloads 10 srms at a time, keeping track of
the number of stalled jobs as well as the number of completed ones. Once
all the requested Subbands have been downloaded, the master script
proceeds to execute the prefactor pipeline.

Because the nodes use a scratch filesystem to hold data during
processing, the running directory is dynamically created and prefactor
has no prior knowledge of the path. To modify prefactor to work in an
arbitrary directory, before running the pipeline, the master script
replaces the Pattern PREFACTOR\_SCRATCH\_DIR with the running directory.

In order to make prefactor easier to run, the input srm file is split
into files holding only one OBSID and the user is asked to choose which
one to run. This makes the separation between calibrator and target run
more natural. On the node, the master script decides whether the
calibrator or target was requested by matching the downloaded files with
the appropriate pattern in the parset. In the case the target was
selected, the calibrator solutions are downloaded and extracted before
the target pipeline is executed. This automates the execution of the
prefactor pipeline on clusters without node-node communication and
minimizes friction with the user.

In the case that the pipeline fails, a snapshot of the entire working
directory is uploaded to storage in case the user wants to start from
the snapshot or do post-mortem debugging.

Surls, Staging and Storage of results
=====================================

LRT Architecture
================
