#!/usr/bin/env python

"""This module creates the launch scripts for the WMS on gina
Options include the number of cores and the queue type."""

import os
import subprocess
import logging
import warnings
import random, string
from shutil import copyfile, rmtree


import tempfile
from GRID_LRT.auth.get_picas_credentials import picas_cred as pc
import GRID_LRT
from GRID_LRT.auth import grid_credentials


#class job_launcher(object):
#    """Generic Job Launcher
#    """
#    def __init__(self):
#        pass

class gridjob(object):
    """A class containing all required descriptions for a SINGLE 
    Grid job, as well as its parameters"""
    def __init__(self, wholenodes=False, NCPU=1, token_type=None):
        self.token_type = token_type
        if wholenodes:
            self.wholenodes = 'true'
        else:
            self.wholenodes = 'false'
        self.ncpu = NCPU       



class RunningJob(object):
    def __init__(self, glite_url=''):
        self.job_status='Unknown'
        self.glite_status='Unknown'
        if glite_url:
            self.glite_url = glite_url
   
    @property
    def status(self):
        self.__check_status()
        return self.job_status

    def __check_status(self):
        glite_process = subprocess.Popen(['glite-wms-job-status', self.glite_url],stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, err = glite_process.communicate()
        try:
            self.job_status=result.split('Current Status:')[1].split()[0]
        except:
            print(err)

        if self.glite_status== 'Running':
            self.count_successes(result)
        if self.glite_status=='Waiting':
            self.count_successes(result)
        if self.glite_status=='Running' and self.job_status=='Waiting':
            self.glite_status='Completed'
            
    def count_successes(self,jobs):
        """Counts the number of Completed jobs in the results of the glite-wms-job-status
        output.  """
        exit_codes=[]
        jobs_list=[]
        for j in jobs.split('=========================================================================='):
            jobs_list.append(j)
        statuses=[]
        for j in jobs_list:
            if "Current Status:" in j:
                statuses.append(j.split("Current Status:")[1].split('\n')[0])
        numdone=0
        for i in statuses:
            if 'Done' in i or 'Cancelled' in i or 'Aborted' in i  :
                numdone+=1
        if 'Done' in statuses[0] or 'Aborted' in statuses[0]:
            self.job_status = 'Done'
        if numdone == len(jobs_list):
            self.job_status='Done'
        if self.job_status == 'Waiting':
            for i in statuses:
                if 'Scheduled' in i:
                    self.job_status = 'Scheduled'
                elif 'Running' in i: 
                    self.job_status = 'Running'
                elif 'Submitted' in i:
                    self.job_status = 'Submitted'
                else:
                    self.job_status = "Done"
        logging.info("Num_jobs_done "+str(numdone)+" snd status is "+self.job_status)
        self.numdone = numdone
        return statuses[1:]

    def __str__(self):
        return "<Grid job '{}' with status '{}'>".format(self.glite_url, self.status)

    def __repr__(self):
        return self.__str__()


class JdlLauncher(object):
    """jdl_launcher creates a jdl launch file with the
    appropriate queue, CPUs, cores and Memory per node

    The jdl file is stored in a temporary location and can be
    automatically removed using a context manager such as:
    >>> with Jdl_launcher_object as j:
        launch_ID=j.launch()
    This will launch the jdl, remove the temp file and reutrn the
    Job_ID for the glite job.
    """

    def __init__(self, numjobs=1, token_type='t_test',
                 parameter_step=4, **kwargs):
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

        self.authorized = False
        if 'authorize' in kwargs.keys() and kwargs['authorize'] == False:
                warnings.warn("Skipping Grid Autorization")
        else: 
	        self.__check_authorized()
        if numjobs < 1:
            logging.warn("jdl_file with zero jobs!")
            numjobs = 1
        self.numjobs = numjobs
        self.parameter_step = parameter_step
        self.token_type = token_type
        self.wholenodes = 'false'

        if 'wholenode' in kwargs:
            self.wholenodes = kwargs['wholenode']
        if "NCPU" in kwargs:
            self.ncpu = kwargs["NCPU"]
        else:
            self.ncpu = 1
        if self.ncpu == 0:
            self.wholenodes = 'true'
        if "queue" in kwargs:
            self.queue = kwargs['queue']
        else:
            self.queue = "medium"
        self.temp_file = None
        self.launch_file = str("/".join((GRID_LRT.__file__.split("/")[:-1])) +
                               "/data/launchers/run_remote_sandbox.sh")

    def __check_authorized(self):
        grid_credentials.grid_credentials_enabled()
        self.authorized = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self.temp_file.name)

    def build_jdl_file(self, database=None):
        """Uses a template to build the jdl file and place it in a
        temporary file object stored internally.
            """
        creds = pc()  # Get credentials, get launch file to send to workers
        if not database:
            database = creds.database
        if not os.path.exists(self.launch_file):
            raise IOError("Launch file doesn't exist! "+self.launch_file)
        jdlfile = """[
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
  ShallowRetryCount = 0;

  Requirements=(RegExp("%s",other.GlueCEUniqueID));
  WholeNodes = %s ;
  SmpGranularity = %d;
  CPUNumber = %d;
]""" % (int(self.parameter_step),
        int(self.numjobs),
        str(database),
        str(creds.user),
        str(creds.password),
        str(self.token_type),
        str(self.launch_file),
        str(self.queue),
        str(self.wholenodes),
        int(self.ncpu),
        int(self.ncpu))
        return jdlfile

    def make_temp_jdlfile(self, database=None):
        """ Makes a temporary file to store the JDL
        document that is only visible to the user"""
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        with open(self.temp_file.name, 'w') as t_file_obj:
            for i in self.build_jdl_file(database):
                t_file_obj.write(i)
        return self.temp_file

    def launch(self, database=None):
        """Launch the glite-job and return the job identification"""
        if not self.authorized:
	        self._check_authorized()
        if not self.temp_file:
            self.temp_file = self.make_temp_jdlfile(database = database)
        sub = subprocess.Popen(['glite-wms-job-submit', '-d', os.environ["USER"],
                                self.temp_file.name], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
        out = sub.communicate()
        if out[1] == "":
            return out[0].split('Your job identifier is:')[1].split()[0]
        raise RuntimeError("Launching of JDL failed because: "+out[1])



class UnauthorizedJdlLauncher(JdlLauncher):
    def __init__(self, *args, **kw):
        super(UnauthorizedJdlLauncher, self).__init__(*args, authorize=False, **kw)

    def launch(self):
        if not self.temp_file:
            self.temp_file = self.make_temp_jdlfile()
        fake_link = 'https://wms2.grid.sara.nl:9000/'+''.join(random.choice(string.ascii_letters + string.digits+"-") for _ in range(22))
        warnings.warn("If you were authorized, we would be launching the JDL here. You'd get this in return: {}".format(fake_link))
        return fake_link


class LouiLauncher(JdlLauncher):
    """
        To make integration tests of an AGLOW step, this job launches it on loui.
    """

    def __init__(self, *args, **kwargs):
        super(LouiLauncher,self).__init__(*args, **kwargs)
        self.return_directory = os.getcwd()
        self.run_directory = tempfile.mkdtemp(prefix='/scratch/') 
        
    def launch(self, database=None):
        copyfile(self.launch_file, self.run_directory+"/run_remote_sandbox.sh")
        os.chdir(self.run_directory)
        creds = pc()
        if not database:
            database = creds.database
        command = "./run_remote_sandbox.sh {} {} {} {}".format(database,
                            creds.user, creds.password, self.token_type)
        os.chmod('run_remote_sandbox.sh',0o744)
        print("Running in folder: ")
        print("")
        print("Don't forget to run LouiLauncher.cleanup() in Pythonwhen you're done!")
        print(self.run_directory)
        with open(self.run_directory+"/stdout.txt","wb") as out:
            with open(self.run_directory+"/stderr.txt","wb") as err:
                launcher = subprocess.Popen(command.split(), stdout=out, stderr=err)
                launcher.wait()
        return {'output':self.run_directory+"/stdout.txt",
                'error':self.run_directory+"/stderr.txt"}

    def __check_authorised(self):
        self.authorized = True
    
    def cleanup(self):
        print("removing directory " + self.run_directory)
        rmtree(self.run_directory)
        os.chdir(self.return_directory)
    
    def __del__(self):
        if os.path.exists(self.run_directory):
            self.cleanup()

    def __exit__(self, exc_type, exc_value, traceback):
        return None
