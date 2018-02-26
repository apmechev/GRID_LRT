import pdb
import os
import shutil
import sys
import yaml
import tempfile
import subprocess
import GRID_LRT
from GRID_LRT import grid_credentials
#TODO: Upload to different locations/methods

class Sandbox(object):

    def __init__(self,cfgfile=None):
        grid_credentials.GRID_credentials_enabled()
        lrt_module_dir=os.path.abspath(GRID_LRT.__file__).split("__init__.py")[0]
        self.base_dir=lrt_module_dir+"Sandbox/" 
        self.return_dir=os.getcwd()
        self.SBXloc=None
        if cfgfile:
            self.parseconfig(cfgfile)

    def __exit__(self):
        if 'remove_when_done' in self.sbx_def.keys():
            if self.sbx_def['remove_when_done']==True:
                self.__cleanup()

    def parseconfig(self,yamlfile):
        with open(yamlfile,'r') as optfile:
            opts_f=yaml.load(optfile)
        self.sbx_def=opts_f['Sandbox']
        self.shell_vars=opts_f['Shell_variables']
        self.tok_vars=opts_f['Token']

    def create_SBX_folder(self,directory=None):
        '''Makes an empty sandbox folder or removes previous one
        '''
        SBX_dir=tempfile.mkdtemp()
        self.tmpdir=SBX_dir
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir)
        else:
            shutil.rmtree(self.tmpdir)
            os.makedirs(self.tmpdir)
        self.enter_SBX_fonder(self.tmpdir)
        self.SBXloc=self.tmpdir
        return self.tmpdir

    def delete_SBX_folder(self,directory=None):
        '''Removes the sandbox folder and subfolders
        '''
        SBX_dir= directory if directory else self.sbx_def['name']
        if os.path.basename(os.getcwd())==self.sbx_def['name']:
            os.chdir(self.base_dir)
        if os.path.exists(self.tmpdir):
            shutil.rmtree(self.tmpdir)

    def enter_SBX_fonder(self,directory=None):
        SBX_dir= directory if directory else self.sbx_def['name']
        if os.path.exists(self.base_dir+SBX_dir):
            os.chdir(self.base_dir+SBX_dir)
       
    def load_git_scripts(self):
        '''Loads the git scripts into the sandbox folder. Top dir names
            are defined in the yaml, not by the git name
        '''
        if os.path.basename(os.getcwd())!=self.tmpdir:
            self.enter_SBX_fonder(self.tmpdir)
        gits=self.sbx_def['git_scripts']
        if not gits: return
        for git in gits:
            clone=subprocess.Popen(['git','clone',gits[git]['git_url'],self.tmpdir+"/"+git])
            clone.wait()
            os.chdir(self.tmpdir+"/"+git)
            if 'branch' in self.sbx_def['git_scripts'].keys():
                checkout=subprocess.Popen(['git','checkout',gits[git]['branch']])
                checkout.wait()
            if 'commit' in self.sbx_def['git_scripts'].keys():
                checkout=subprocess.Popen(['git','checkout',gits[git]['commit']])
                checkout.wait()
            os.chdir(self.tmpdir+"/")

    def copy_git_scripts(self):
        SBX_type = self.sbx_def['git']['branch']
        SBX_dir = self.sbx_def['name']
        print("Checking out Sanbox repository")
        print("")
        subprocess.call('git clone   ' +self.sbx_def['git']['location']+ " "+ self.tmpdir,shell=True) 
        os.chdir(self.tmpdir)
        checkout=subprocess.Popen(['git','checkout',self.sbx_def['git']['branch']])
        checkout.wait()
        print("")

    def copy_base_scripts(self,basetype=None):
        if 'git' in self.sbx_def:
            self.copy_git_scripts()
        else:
            self.copy_local_scripts(basetype)

    def copy_local_scripts(self,basetype):
        SBX_type = basetype if basetype else self.sbx_def['type']
        SBX_dir = self.sbx_def['name']
        scripts_path=self.base_dir+'/scripts/'+SBX_type
        if os.path.exists(scripts_path):
            subprocess.call('cp -r '+scripts_path+"/* "+self.tmpdir,shell=True)


    def git_base_scripts(self,gitrepo=None):
        ''' Can pull the default scripts from a git repository
            
    '''
        SBX_dir = self.sbx_def['name']
        scripts_path=self.base_dir+'/scripts/'+SBX_type
        if os.path.exists(scripts_path):
            clone=subprocess.Popen(['git','clone',gitrepo,'git_base_scripts'])
            clone.wait()
            subprocess.call('mv '+'git_base_scripts'+"/* "+self.tmpdir,shell=True)

    def upload_SBX(self,SBXfile=None,loc=None,upload_name=None):
        self.upload_gsi_SBX(SBXfile,loc,upload_name)
        self.upload_gsi_SBX(SBXfile,upload_name=upload_name,loc=' gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/sandbox')

    def upload_ssh_sandbox(self,SBXfile=None,loc=None,upload_name=None):
        gsiloc='/disks/ftphome/pub/apmechev/sandbox/'
        rename=self.tarfile

        if not upload_name:
            if not ".tar" in rename:
                rename=rename+".tar"
            upload_name=rename 

        upload_place=gsiloc+self.sbx_def['loc']
        if self.tarfile:
            upload=subprocess.Popen(['scp',self.tarfile, "gaasp:"+gsiloc+
                                    self.sbx_def['loc']+"/"+upload_name])
            upload.wait()


    def upload_gsi_SBX(self,SBXfile=None,loc=None,upload_name=None): #TODO: Use UL/DL interfaces
        """ Uploads the sandbox to the relative folders
        """
        gsiloc='gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/sandbox/'
        if self.sandbox_exists(gsiloc+self.sbx_def['loc']+"/"+self.tarfile):
            self.delete_gsi_sandbox(gsiloc+self.sbx_def['loc']+"/"+self.tarfile)

        rename=self.tarfile

        if not upload_name:
            if not ".tar" in rename:
                rename=rename+".tar"
            upload_name=rename 

        upload_place=gsiloc+self.sbx_def['loc']
        if loc is not None: upload_place=loc
        print(upload_place)
        
        if self.tarfile:
            upload=subprocess.Popen(['globus-url-copy',self.tarfile, gsiloc+
                                    self.sbx_def['loc']+"/"+upload_name])
        upload.wait()
        print("Uploaded sandbox to "+gsiloc+self.sbx_def['loc']+"/"+upload_name)
        self.SBXloc=self.sbx_def['loc']+"/"+upload_name 


    def sandbox_exists(self,sbxfile):
        file1=subprocess.Popen(['uberftp','-ls',sbxfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output=file1.communicate()
        if output[0]!='' and output[1]=='':
            return True
        return False


    def delete_gsi_sandbox(self,sbxfile):
        deljob=subprocess.Popen(['uberftp','-rm',sbxfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print("deleted old sandbox")
        return deljob.communicate()


    def zip_SBX(self,zipname=None):
        filename=zipname if zipname else self.sbx_def['name']+".tar"
        print(filename)
        tar=subprocess.call('tar -cf '+filename+' *',shell=True)
        self.tarfile=filename


    def cleanup(self):
        self.delete_SBX_folder()
        os.chdir(self.return_dir)
        pass

    def make_tokvar_dict(self):
        tokvardict=self.shell_vars
        yaml.dump(tokvardict,open('tokvar.cfg','wb'))
        pass

    def check_token(self):
        '''This function does the necessary linkage between the sandbox and token
           most importantly it saves the tokvar.cfg file in the sbx, but also checks
           if the token variables are all existing. If so, tokvar is created and put
           inside the SBX
        '''
        token_vars=self.tok_vars
        for key in self.shell_vars:
            if key in token_vars.keys():
                pass
            else:
                print(key+" missing")
        self.make_tokvar_dict()

    def get_result_loc(self):
        return (self.sbx_def['results']['UL_loc'] +
                "".join(self.sbx_def['results']['UL_pattern']))
 

    def build_sandbox(self,sbx_config):
        """A comprehensive function that builds a Sandbox from a configuration file and creates a 
        sandbox tarfile. 
           
        """
        self.parseconfig(sbx_config)
        self.create_SBX_folder()
        self.enter_SBX_fonder()
        self.copy_base_scripts()
        self.load_git_scripts()
        self.make_tokvar_dict()
        self.zip_SBX()


    def upload_sandbox(self,upload_name=None):
        self.upload_SBX(upload_name=upload_name)
        self.upload_ssh_sandbox(upload_name=upload_name)
        if self.sbx_def['remove_when_done'] == 'True':
            self.cleanup()
