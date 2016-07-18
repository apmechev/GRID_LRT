# Spectroscopy

The following grid solution is designed/developed by Natalie Danezi (<anatoli.danezi@surfsara.nl>) and Coen Schrijvers (<coen.schrijvers@surfsara.nl>) 
as a template example for porting the Spectroscopy application (e-infra130159 request, Raymond Oonk <oonk@astron.nl>) to the Grid.


## Overview


### Application Design

The design of this approach is based on the following basic elements:

* We have a number of **tasks** (Spectroscopy application) to be processed on the Grid Worker Nodes.  
* Each task requires a set of parameters to run. The parameters of each task (observation id, input files, etc) construct an individual piece of work, 
called **token**. *NB the token is just a description not the task itself.*  
* This approach launches a number of Grid jobs called **pilot jobs**, smaller than the number of tasks. The pilot jobs run in parallel.  
* Each pilot job is like a normal job, but instead of executing the task directly it asks for the next task from a central repository once it is 
running on a worker node. A task corresponds to one token. *NB only one client can work on any token at any one time.*  
* A pilot job terminates when no more tokens are available.  

This approach is based on a wrapper script for the arrangement of subsequent Spectroscopy runs (tasks) on the grid, making use of the PiCaS job 
management system. The procedure consists of the following 3 steps:

1. [Tokens - PiCaS pool server](#Tokens): the user generates a number of tokens and uploads these to the central repository (PiCaS token pool).  
2. [Staging - Pin files on disk](#Staging): the user stages the required input files from tape to disk.  
3. [Application - Run Pilot Jobs](#Application): the user submits pilot jobs to the Grid Worker Nodes.  
    Pilot job workflow:
    * Makes a connection to the PiCaS server and gets the next available token.
    * Runs a wrapper script to execute a task with the parameters fetched from the token. The wrapper script ( *master_step23.sh* ):
        * Sets the LOFAR environment on the Worker Node
        * Extracts the Calibrator data from Grid storage (fifo) and runs *ms_reduc_cal_3c196_v3.py* (step 2)
        * Extracts Source data from Grid storage (fifo) and runs *ms_apply_src_fspc_v3.py* (step 3)
        * Compresses the images output ( *restored.corr* ) and copies the output to the Grid storage here:  
 `srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/`
    * Attaches the log files to the corresponding token when the task is done.
    * Asks for the next available token or dies if there is no other token left.  

The following sections cover some useful background information for the tools and design concepts used in this approach. To execute the steps as they come, go directly to 
the *hands on* part in section [Running the solution](#Handson).


### PiCaS Framework

The central repository for the tasks is PiCaS, a Token Pool Server. The pilot jobs request the next free token for processing from PiCaS. 
*NB the content of the tokens is opaque to PiCaS and can be anything our application needs.*

PiCaS works as a queue, providing a mechanism to step through the work one token at a time. It is also a pilot job system, indicating that the client 
communicates with the PiCaS server to fetch work, instead of having that work specified in a jdl (or similar) file.  

The server is based on CouchDB (NoSQL database) and the client side is written in Python.  

* PiCaS Server:

>On the server side we have a queue which keeps track of which tokens are available, locked or done. This allows clients to easily retrieve new pieces 
of work and allows also easy monitoring of the resources. As every application needs different parameters, the framework has a flexible data structure 
that allows users to save different types of data. PiCaS system is easily accessible from anywhere, as it might not be known beforehand where the 
resources are located.

>PiCaS server is based on CouchDB. CouchDB stores documents which are self-contained pieces of information. These documents support a dynamic data 
model, so unlike traditional databases, CouchDB allows storing and retrieving any piece of information as long as it can be defined as key-value 
pairs. This feature is used  to store all the information needed to keep track of the job stages and all of the required in- and outputs.

>CouchDB also provides a Restful API, which means that we can easily access information with an http client. This can be a browser, a commandline 
application like curl or a complete client library. It is also possible to interact with PiCaS using the web-interface. This interface comes included 
with the normal distribution. 

* Picas Client:  

>The PiCaS client library was created to ease communication with the CouchDB back-end. It allows users to easily fetch, modify and upload tokens. 
The system has been implemented as a Python Iterator, which basically means that that the application is one large for loop that keeps on running as 
long as there is work to be done. The client is written in Python and uses the python couchdb module, which requires at least python version 2.6. The 
client library is constructed using a number of modules and classes, most important of these are:  

>    * The *Actors* module contains the RunActor class. This is the class that has to be overwritten to include the code that calls the different 
applications (tasks) to run.
>    * The *Clients* module contains a CouchClient class that creates a connection to CouchDB.  
>    * The *Iterators* module contains classes responsible for working through the available tokens. The BasicViewIterator class assumes that all the token 
information is encoded directly into the CouchDB documents.  
>    * The *Modifiers* module is responsible for modification of the PiCaS tokens. It makes sure the tokens are modified in a uniform way.  


### Design workflow

The approach described here is enacted with the following development steps:

* Define and generate the Spectroscopy tokens with all the necessary parameters.  
* Define and create a master shell script ( *master_step23.sh* ) that will be send with the job using the input sandbox. This contains some boiler 
plate code to e.g. setup the environment, download software or data from a SRM, run the application etc. This doesn’t have to be a shell script, 
however, setting up environment variables is easiest when using a shell script, and this way setup scripts are separated from the application code.  
* Define and create a python script to handle all the communication with the token pool server, call the master script, catch errors and do the reporting.   
* Define the jdl on the user interface machine to specify some general properties of your jobs. This is required to submit a batch of pilot jobs to 
the Grid that will in turn initiate the python script as defined in the previous step.  


### Spectroscopy Tokens

Each token uploaded to the PiCaS server for the Spectroscopy tasks has the following form:
  
>   *id*: token ID  
>   *type*: token  
>   *lock*: timestamp set when the token is fetched for processing (initial value is 0)  
>   *done*: timestamp set when the token has been successfully processed (initial value is 0)  
>   *scrub_count*: counter that increases every time the token is reset (initial value 0)  
>   *hostname*: will be replaced with the worker node hostname  
>   *obsID*: Observation ID   
>   *SURL_cal*: SRM path of grid directory of Calibrator input dataset  
>   *SURL_src*: SRM path of grid directory of Source input dataset  
>   *output*: the exit code of the job    
>   *attachments*: stdout, sterr and log files per job 
>   *calavgc*: configuration parameter  
>   *calavgt*: configuration parameter  	
>   *freqres*: configuration parameter  
>   *sbfactor*: configuration parameter  
>   *rcavgc*: configuration parameter  	
>   *srcavgt*: configuration parameter   	
>   *subband_cal*: configuration parameter  
>   *subband_src*: configuration parameter


<a id="Handson"/>
## Running the solution (Spectroscopy_v6)


### Prerequisites

To be able to run the Spectroscopy solution, a user must have:

* An account on the Lofar User Interface machine `loui.grid.sara.nl` (send your request to <grid.support@surfsara.nl>)
    * Users with an account on the common User Interface machine `uimd.grid.sara.nl`, can use this for submitting the jobs, but not for debugging the solution (Lofar software is not installed on `uimd`)  
* A Grid certificate: instructions [here](https://grid.surfsara.nl/wiki/index.php/Using_the_Grid/Getting_a_Grid_certificate)  
* A VO membership for Lofar VO: instructions [here](https://grid.surfsara.nl/wiki/index.php/Using_the_Grid/VO_membership)  
* An account on PiCaS server (send your request to <grid.support@surfsara.nl>)  


### Preparation

Login to the Lofar User Interface machine:  
`$ ssh <username>@loui.grid.sara.nl`

Get the solution scripts from here: `spectroscopy_v6.tar`  

Decompress the file:  
`$ tar -xf spectroscopy_v6.tar`  

This creates a directory **spectroscopy_v6**.  

List the contents of *spectroscopy_v6* directory.  
`$ cd spectroscopy_v6/`  
`$ ls -l`
>   `readme.md`    
    `Tokens/`       
    `Staging/`   
    `Application/` 

Detailed information regarding the operations performed in each of the scripts below is embedded to the comments inside each of the scripts individually.  


<a id="Tokens"/>
### 1. Tokens - PiCaS pool server    

Move to the Tokens directory':  
`$ cd Tokens`

List the files in Tokens directory:  
`$ ls -l`
>   `createTokens.py`  
    `createViews.py`  
    `createObsIDView.py`    
    `resetLockedTokens.py`  
    `resetErrorTokens.py`  
    `picas/`        #[picas client repository](https://github.com/jjbot/picasclient)  
    `couchdb/`      #[python library for couchdb - current v0.9](https://pypi.python.org/pypi/CouchDB)  
    `datasets/`     #includes obsID directories with the necessary srmpath/subband/setup.cfg files, e.g. L96650  

* Upload the Tokens:  
`$ python createTokens.py [obsID] $PICAS_DB $PICAS_USR $PICAS_USR_PWD`   
>   Replace [obsID] with the pre-configured Observation dataset. Example:  
    `$ python createTokens.py L96650 $PICAS_DB $PICAS_USR $PICAS_USR_PWD`  
    `$ python createTokens.py L86280 $PICAS_DB $PICAS_USR $PICAS_USR_PWD` 

* Create the Views (pools) - independent to [obsID]:  
`$ python createViews.py $PICAS_DB $PICAS_USR $PICAS_USR_PWD`
    
* Optionally create separate views to group the observations  
`$ python createObsIDView.py [obsID] $PICAS_DB $PICAS_USR $PICAS_USR_PWD`
>   Replace [obsID] with the Observation specific token name. Example:  
    `$ python createObsIDView.py L86280 $PICAS_DB $PICAS_USR $PICAS_USR_PWD`  
    `$ python createObsIDView.py L96650 $PICAS_DB $PICAS_USR $PICAS_USR_PWD`  

* Reset tokens that are locked or in error state (when needed):  
`$ python resetLockedTokens.py $PICAS_DB $PICAS_USR $PICAS_USR_PWD`  
`$ python resetErrorTokens.py $PICAS_DB $PICAS_USR $PICAS_USR_PWD`  


<a id="Staging"/>
### 2. Staging - Pin files on disk  

Move to the Staging directory':  
`$ cd ../Staging`

List the files in Staging directory:  
`$ ls -l`
>   `state.py`       
    `stage.py`       
    `pythonpath.py`   #fixed file to enable gfal   
    `datasets/`       #same directory as in step [1. Tokens - PiCaS pool server](#Tokens)   

* Create a proxy:  
`$ startGridSession lofar:/lofar/user`  

* Convert files with srm paths to the necessary format : /pnfs/grid.sara.nl/...   
`$ sed -e "s/srm:\/\/srm.grid.sara.nl:8443//" datasets/[obsID]/srmlist > files`  
>   Replace [obsID] with the Observation specific ID. Example:  
    * for SURFsara:  
`$ sed -e "s/srm:\/\/srm.grid.sara.nl:8443//" datasets/L86280/srmlist > files`  
    * for Juelich -- under construction:  
`$ sed -e "s/srm:\/\/lofar-srm.fz-juelich.de:8443//" datasets/L96650/srmlist > files`  

* Check whether the files are NEARLINE_and_ONLINE (both on tape and disk):  
`$ python state.py`

* Stage the files that are not ONLINE (specify pin lifetime parameter:srmv2_desiredpintime):  
`$ python stage.py`


<a name="Application"/>
### 3. Application - Run Pilot Jobs

Move to the Staging directory':  
`$ cd ../Application`

List the files in Staging directory:  
`$ ls -l`
>   `spectroscopy.jdl`   
    `sandbox/`  

`$ ls -l sandbox/`  
>   `picas.tar`     #[picas client repository](https://github.com/jjbot/picasclient)   
    `couchdb.tar`   #[python library for couchdb - current v0.9](https://pypi.python.org/pypi/CouchDB)   
    `scripts.tar`      #includes all the Spectroscopy specific scripts  
    `startpilot.sh`  
    `pilot.py`  
    `master_step23.sh`  

* Submit the pilot jobs:  

>   a) Execution on `loui.grid.sara.nl` for debugging (or other machine with the LOFAR software on board and python >=2.6):  
`$ cd sandbox/`  
`$ . startpilot.sh $PICAS_DB $PICAS_USR $PICAS_USR_PWD &`  

>   b) Execution on GRID:   

>>  1. Create a proxy:  
    `$ startGridSession lofar:/lofar/user`  

>>  2. Modify *spectroscopy.jdl* by replacing [$PICAS_DB] [$PICAS_USR] [$PICAS_USR_PWD] with your credentials (hard-coded).  

>>  3. Submit the jobs to the Grid   
    `$ glite-wms-job-submit -d $USER -o jobIDs spectroscopy.jdl`


### Additional info:

* Current datasets/[obsID] directory:
> `datasets/srmlist`          #contains the list with SURLS of input data for the corresponding observation ID   
> `datasets/subbandlist`      #contains the subband list for the corresponding observation ID   
> `datasets/setup.cfg`        #contains the configuration parameters for the corresponding observation ID   

* Usage of *master_step23_v3.sh*:  
`$ ./master_step23.sh [OBSID] [SUBBAND_CAL] [SUBBAND_SRC] [SURL_CAL] [SURL_SRC] [FREQRES] [CALAVGC] [CALAVGT] [SRCAVGC] [SRCAVGT] 2> logs_[OBSID]_[SUBBAND_CAL]_[SUBBAND_SRC].err 1> logs_[OBSID]_[SUBBAND_CAL]_[SUBBAND_SRC].out &`
>   Example:  
    `$ ./master_step23.sh L86280 SAP001_SB186 SAP000_SB064 srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc0_032/86280/L86280_SAP001_SB186_uv.MS_9871bda8.tar srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc0_032/86280/L86280_SAP000_SB064_uv.MS_de02aef2.tar 64 64 1 2 1 2> logs_L86280_SAP001_SB186_SAP000_SB064.err 1> logs_L86280_SAP001_SB186_SAP000_SB064.out &`  

* Checking the output on Grid storage:  
 `$ srmls srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/`  

* Download the output from Grid storage locally:  
`$ srmcp -server_mode=passive srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/[OBSID dir]/[tar output] file:///$PWD/[tar output]`   
>   Example:  
    `$ srmcp -server_mode=passive srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/user/disk/spectroscopy/L86280_SAP001_SB186_SAP000_SB064/L86280_SAP000_SB064_uv.MS.fs.msc.img.tar file:///$PWD/L86280_SAP000_SB064_uv.MS.fs.msc.img.tar`

* Optionally get the parametric job outputSandbox:   
`$ glite-wms-job-output --dir . -i jobIDs`  


## Useful links

1. Pilot jobs overview: [SURFsara wiki page](https://grid.surfsara.nl/wiki/index.php/Using_the_Grid/ToPoS)   
2. Pilot Job Frameworks: [SURFsara mooc video lecture](https://www.youtube.com/watch?v=uHSsKJ6xPcs&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=29)  
3. PiCaS Server side (part I): [SURFsara mooc video lecture](https://www.youtube.com/watch?v=PDRe7i0SGlE&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=30)  
4. PiCaS Server side (part II): [SURFsara mooc video lecture](https://www.youtube.com/watch?v=uiHTG3Cr0zM&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=31)  
5. PiCaS Client side: [SURFsara mooc video lecture](https://www.youtube.com/watch?v=c6ETyoKWjw4&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=32)  
6. PiCaS Practice (part I): [SURFsara mooc video lecture](https://www.youtube.com/watch?v=PwDpplql9EA&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=33)  
7. PiCaS Practice (part II): [SURFsara mooc video lecture](https://www.youtube.com/watch?v=DJ6vHERy-qY&list=PLvgGDb8k0n2cgWL01fsxkMAo4_Ewvc74A&index=34)  
8. CouchDB: [Official website](http://couchdb.apache.org/)
9. CouchDB book: [The Definitive Guide](http://guide.couchdb.org/)  

--  
        Anatoli Danezi, SURFsara 28/07/2014  
---