import os
import shutil
import sys
import yaml
import subprocess

class Sandbox(object):

    def __init__(self,yamlfile=None):
        self.base_dir=os.getcwd()+"/"
        self.SBXloc=None
        if yamlfile:
            self.parseconfig(yamflile)

    def __exit__(self):
        if 'remove_when_done' in self.options['sandbox'].keys():
            if self.options['sandbox']['remove_when_done']==True:
                self.cleanup()

    def parseconfig(self,yamlfile):
        try:
            with open(yamlfile,'rb') as optfile:
                opts_f=yaml.load(optfile)
        except yaml.YAMLError as exc:
            print(exc)
        self.options=opts_f    

    def create_SBX_folder(self,directory=None):
        '''Makes an empty sandbox folder or removes previous one
        '''
        SBX_dir= directory if directory else self.options['sandbox']['name']
        if not os.path.exists(SBX_dir):
            os.makedirs(SBX_dir)
        else:
            shutil.rmtree(SBX_dir)
            os.makedirs(SBX_dir)

    def delete_SBX_folder(self,directory=None):
        '''Removes the sandbox folder and subfolders
        '''
        SBX_dir= directory if directory else self.options['sandbox']['name']
        if os.path.basename(os.getcwd())==self.options['sandbox']['name']:
            os.chdir(self.base_dir)
        if os.path.exists(SBX_dir):
            shutil.rmtree(SBX_dir)

    def enter_SBX_folder(self,directory=None):
        SBX_dir= directory if directory else self.options['sandbox']['name']
        if os.path.exists(SBX_dir):
            os.chdir(SBX_dir)
       
    def load_git_scripts(self):
        '''Loads the git scripts into the sandbox folder. Top dir names
            are defined in the yaml, not by the git name
        '''
        if os.path.basename(os.getcwd())!=self.options['sandbox']['name']:
            self.enter_SBX_folder()
        gits=self.options['sandbox']['git_scripts']
        for git in gits:
            clone=subprocess.Popen(['git','clone',gits[git]['git_url'],git])
            clone.wait()
            os.chdir(git)
            if 'branch' in self.options['sandbox']['git_scripts'].keys():
                checkout=subprocess.Popen(['git','checkout',gits[git]['branch']])
                checkout.wait()
            if 'commit' in self.options['sandbox']['git_scripts'].keys():
                checkout=subprocess.Popen(['git','checkout',gits[git]['commit']])
                checkout.wait()
            os.chdir('..')

    def copy_base_scripts(self,basetype=None):
        SBX_type = basetype if basetype else self.options['sandbox']['type']
        SBX_dir = self.options['sandbox']['name']
        scripts_path=self.base_dir+'/scripts/'+SBX_type
        if os.path.exists(scripts_path):
            subprocess.call('cp -r '+scripts_path+"/* "+self.base_dir+SBX_dir,shell=True)


    def upload_SBX(self,SBXfile=None,loc=None): #TODO: Use UL/DL interfaces
        if self.sandbox_exists(self.options['sandbox']['loc']+"/"+self.tarfile):
            self.delete_sandbox(self.options['sandbox']['loc']+"/"+self.tarfile)
        if self.tarfile:
            upload=subprocess.Popen(['globus-url-copy',self.tarfile,
                                    self.options['sandbox']['loc']+"/"+self.tarfile])
        upload.wait()
        print("Uploaded sandbox to "+self.options['sandbox']['loc']+"/"+self.tarfile)
        self.SBXloc=self.options['sandbox']['loc']+"/"+self.tarfile


    def sandbox_exists(self,sbxfile):
        file1=subprocess.Popen(['uberftp','-ls',sbxfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output=file1.communicate()
        if output[0]!='' and output[1]=='':
            return True
        return False


    def delete_sandbox(self,sbxfile):
        deljob=subprocess.Popen(['uberftp','-rm',sbxfile],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        print "deleted old sandbox"
        return deljob.communicate()


    def zip_SBX(self,zipname=None):
        filename=zipname if zipname else self.options['sandbox']['name']+".tar"
        print filename
        tar=subprocess.call('tar -cf '+filename+' *',shell=True)
        self.tarfile=filename


    def cleanup(self):
        self.delete_SBX_folder()
        pass

    def make_tokvar_dict(self):
        tokvardict=self.options['tokvar']
        yaml.dump(tokvardict,open('tokvar.cfg','wb'))
        pass

    def check_token(self,tok_cfg='token_config.cfg'):
        '''This function does the necessary linkage between the sandbox and token
           most importantly it saves the tokvar.cfg file in the sbx, but also checks
           if the token variables are all existing. If so, tokvar is created and put
           inside the SBX
        '''
        token_vars=yaml.load(open(tok_cfg,'rb'))
        for key in self.options['tokvar']:
            if key in token_vars.keys():
                pass
            else:
                print(key+" missing")
        self.make_tokvar_dict()

    def get_result_loc(self):
        return (self.options['results']['UL_loc'] +
                "".join(self.options['results']['UL_pattern']))

