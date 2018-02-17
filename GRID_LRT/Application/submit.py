#!/usr/bin/env python

"""This module creates the launch scripts for the WMS on gina
Options include the number of cores and the queue type."""
import pdb
import tempfile
from GRID_LRT.get_picas_credentials import picas_cred as pc
import os
import subprocess
import GRID_LRT
from GRID_LRT import grid_credentials


class job_launcher(object):
    def __init__(self):
        pass

class jdl_launcher(object):
    """jdl_launcher creates a jdl launch file with the 
    appropriate queue, CPUs, cores and Memory per node
    
    The jdl file is stored in a temporary location and can be 
    automatically removed using a context manager such as:
    >>> with Jdl_launcher_object as j:
        launch_ID=j.launch()
    This will launch the jdl, remove the temp file and reutrn the 
    Job_ID for the glite job. 
    """

    def __init__(self,numjobs=1,token_type='t_test',wholenodes=False,parameter_step=4,*args,**kwargs):
        """The jdl_launcher class is initialized with the number of jobs, 
        the name of the PiCaS token type to run, and a flag to use the whole node.
        

         Args:
            numjobs (int): The number of jobs to launch on the cluster 
            token_type (str): The name of the token_type to launch from the 
                PiCaS database. this uses the get_picas_credentials module to 
                get the PiCaS database name, uname, passw
            wholenodes(Boolean): Whether to reserve the entire node. Default is F
            NCPU (int, optional): Number of CPUs to use for each job. Default is 1
        """
        grid_credentials.GRID_credentials_enabled()
        if numjobs<1:
            logging.warn("jdl_file with zero jobs!")
            numjobs=1
        self.numjobs=numjobs
        self.parameter_step=parameter_step
        self.token_type=token_type
        if wholenodes:
            self.wholenodes='true'
        else:
            self.wholenodes='false'
        if "NCPU" in kwargs:
            self.NCPU= kwargs["NCPU"]
        else: 
            self.NCPU=1
        if "queue" in kwargs:
            self.queue=kwargs['queue']
        else:
            self.queue="mediummc"
        self.temp_file=None

    def __enter__(self):
        return self

    def __exit__(self,exc_type, exc_value, traceback):
        os.remove(self.temp_file.name)

    def build_jdl_file(self):
        """Uses a template to build the jdl file and place it in a 
        temporary file object stored internally. 
            """
        creds=pc()  # Get credentials, get launch file to send to workers
        self.launch_file=str("/".join((GRID_LRT.__file__.split("/")[:-1]))+
                        "/Sandbox/launchers/run_remote_sandbox.sh")
        if not os.path.exists(self.launch_file):
            raise IOError("Launch file doesn't exist! "+self.launch_file)
        jdlfile="""[
  JobType="Parametric";
  ParameterStart=0;
  ParameterStep=%d;                                                                                      
  Parameters= %d ;
  Executable = "/bin/sh";

  Arguments = "run_remote_sandbox.sh %s %s %s %s ";
  Stdoutput = "parametricjob.out";
  StdError = "parametricjob.err";
  InputSandbox = {"%s"};
  OutputSandbox = {"parametricjob.out", "parametricjob.err"};
  DataAccessProtocol = {"gsiftp"};
  ShallowRetryCount = 5;

  Requirements=(RegExp("%s",other.GlueCEUniqueID));
  WholeNodes = %s ;
  SmpGranularity = %d;
  CPUNumber = %d;
]"""%(  int(self.parameter_step),
        int(self.numjobs),
        str(creds.database),
        str(creds.user),
        str(creds.password),
        str(self.token_type),
        str(self.launch_file),
        str(self.queue),
        str(self.wholenodes),
        int(self.NCPU),
        int(self.NCPU))  
        return jdlfile

    def make_temp_jdlfile(self):
        self.temp_file=tempfile.NamedTemporaryFile(delete=False)
        with self.temp_file as t_file_obj:
            for i in self.build_jdl_file():
                t_file_obj.write(i)
        return self.temp_file

    def launch(self):
        if not self.temp_file:
            self.temp_file=self.make_temp_jdlfile()
        sub=subprocess.Popen(['glite-wms-job-submit','-d',os.environ["USER"],self.temp_file.name], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out=sub.communicate()
        if out[1]=="":
            return out[0].split('Your job identifier is:')[1].split()[0]
        raise RuntimeError("Launching of JDL failed because: "+out[1])
