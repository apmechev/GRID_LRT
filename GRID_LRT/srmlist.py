import sys
import re
import os
import subprocess
from GRID_LRT import gsurl
import GRID_LRT.Staging.stage_all_LTA as stage_all
import GRID_LRT.Staging.state_all as state_all
import GRID_LRT.Staging.stager_access as sa

import pdb

class srm_manager(object):
    def __init__(self,OBSID="",filename="",stride=1):
        """Initializes the srmlist object. The stride is how many tokens to make
            stride=1 makes token for each link, stride 10 groups by 10, etc
            The self.srms dictionary is what is used later by the default_LRT
            to make the tokens and possibly to rearrange the links by real frequency
        """
        self.OBSID = OBSID
        self.filename = filename
        self.stride = stride
        self.srms = {} #A dictionary of {SBN,surl} TODO: Maybe use ABN_list for all srms: tokens will be made with key:value
        self.ABN_list = {} #A dictionary of {SBN:[srm1,srm2,srm3]} 
        self.stageIS=None
        if filename and OBSID: #With arbitrary # of srms per token
            self.file_load(filename, OBSID)
        elif filename:
            self.file_load(filename)


    def __iter__(self):
        self.keys=self.srms.keys()
        self.loc=0
        return self

    def next(self):
        if self.loc < len(self.keys):
            tmp=self.keys[self.loc]
            self.loc+=1
            return self.srms[tmp]
        raise StopIteration

    __next__=next


    def file_load(self,filename,OBSID=""):
        """Loads a list of srms from a file by searching the file for 
            1. The OBSID class is initiated
            2. The OBSID given by this function
            3. The first OBSID encountered in the file
            After, the script only loads the lines that contain the OBSID
            into the dict srms
        """
        self.filename=filename
        if self.OBSID=="" and OBSID!="":
            self.OBSID=OBSID
        self.check_OBSID()
        
        sys.path.append('LRT/gsurl')
        self.srms=gsurl.make_list_of_surls(self.filename,self.stride) 

        f1=open(self.filename,'r').read()
        #TODO: make a srmlist class where fixsrms is builtin
        if "fz-juelich.de" in f1:
            self.fix_srms('srm:\/\/lofar-srm.fz-juelich.de:8443')
        elif "srm.grid.sara.nl" in f1:
            self.fix_srms('srm:\/\/srm.grid.sara.nl:8443')
        elif "lofar.psnc.pl" in f1:
            self.fix_srms('srm:\/\/lta-head.lofar.psnc.pl:8443')
        

    def make_abndict_from_tokens(self,token_type,location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP/"):
        '''Makes a Dictionary of ABNs taken from the completed tokens 
        '''
        self.location=location
        s_ABN=self.get_ABN_list_from_token(token_type)
        ABN_files=self.make_url_list(location)
        return self.make_list(s_ABN,ABN_files,"AB")

    def make_sbndict_from_gsidir(self,location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP/"):
        self.location=location
        gsi_files=self.make_gsi_list(location)
        files=[]
        for i in gsi_files:
            files.append(i.split(location)[1])
        return self.make_list([[1],[244]],files,"_")

    def make_sbndict_from_file(self,filename):
        '''Makes a Dictionary of ABNs taken from the completed tokens 
        '''
        self.srms=gsurl.make_list_of_surls(filename,1)
        SBN_files=[]
        for key, value in self.srms.iteritems():
            SBN_files.append(os.path.basename(value))
        s_SBN=sorted(self.srms.keys())
        self.location=os.path.dirname(value)
        return self.make_list(s_SBN,SBN_files,'SB')


    def make_list(self,SBs,files,append='SB'):
        """Makes a dictionary of links keyed with the starting SBN, ABN
        """
        for chunk in range(0,(SBs[-1][0]-SBs[0][0])/self.stride+1):
            try:
                abn=SBs[0][0]+chunk*self.stride
            except IndexError:
                continue # Not sure why this happens
            abn_files=[]
        
            for abnum in range(self.stride):
                try:
                    abn_files.append(self.location+"/"+str([x for x in files if append+str("%03d" % (abn+abnum)) in x][0]))
                except IndexError:
                    continue
            ##TODO: SB021 has zero padding!
            self.ABN_list["%03d" % abn]=abn_files
        return self.ABN_list



    def get_ABN_list_from_token(self,token_type):
        '''Takes all the done tokens and makes a list of ABNs (Absolute Subband Num)
            That are available. Sorts them 
        '''
        import Token
        th=Token.Token_Handler(uname=os.environ["PICAS_USR"],pwd=os.environ["PICAS_USR_PWD"],
                                dbn=os.environ["PICAS_DB"],t_type=token_type)
        print th.t_type
        v=th.db.view(th.t_type+"/"+"done")
        sbns=[]
        for x in v:
            ifth.db[x["id"]["pipeline"]=='pref_targ1':
                if th.db[x["id"]]["ABN"]=="":
                    continue
                sbns.append((int(th.db[x["id"]]["ABN"]),th.db[x["id"]]["start_SB"]))
        sorted_ABNs=sorted(sbns, key=lambda x: x[0])
        return sorted_ABNs


    def make_url_list(self,location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP"):
        self.location=location+"/"+self.OBSID
        urls=subprocess.Popen(["uberftp","-ls",location+"/"+self.OBSID+"/t1_"+self.OBSID+"_AB*"],
                                stdout=subprocess.PIPE)
        tmp_urls=urls.communicate()[0].split('\n')[:-1]
        filenames=[]
        for url in tmp_urls:
            filenames.append(url.split()[-1].split(self.OBSID+"/")[1])    
        return sorted(filenames) 

    def make_gsi_list(self,location="gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP"):
        self.location=location
        urls=subprocess.Popen(["uberftp","-ls",location+"/*"],
                                stdout=subprocess.PIPE)
        tmp_urls=urls.communicate()[0].split('\n')[:-1]
        filenames=[]
        for url in tmp_urls:
            filenames.append(location+url.split()[-1].split("/")[-1])
        return sorted(filenames)


    def check_OBSID(self):
        """If the OBSID is empty, it takes the first OBSID from the file
            Otherwise it checks if the OBSID exists in the file
            If more than one OBSIDs in the file, it makes a new one and
            sets self.filename to that
        """
        if self.OBSID=="":
            with open(self.filename,'r') as txtfile:
                line=txtfile.readline()
                self.OBSID='L'+str(re.search("L(.+?)_",line).group(1))
            if self.OBSID=="":
                print "Sorry. could not get OBSID"
                raise KeyError
        found=False

        #Tests if only one OBSID in file 
        with open(self.filename,'rt') as f:
            for line in f:
                if self.OBSID in line:
                    found=True
                else:
                    lines=open(self.filename,'r').readlines()
                    with open(self.OBSID+".txt",'w') as file1:
                        [file1.write(x) for x in lines if self.OBSID in x]
                    self.filename=self.OBSID+".txt"
        if not found:
            print "\033[31mOBSID not found in SRM file!\033[0m"
            sys.exit()


    def state(self,printout=True): 
        self.states=state_all.state_dict(self.srms,printout=printout)
        return self.states


    def stage(self):
        self.stageID=stage_all.state_dict(self.srms)


    def get_stage_status(self):
        if not self.stageID:
            self.stage()
        print(str(sa.get_progress().get(str(self.stageID))['Percent done'])+" Percent Done")
        self.percent_done=float(sa.get_progress().get(str(self.stageID))['Percent done'])
        return stage_all.get_stage_status(self.stageID)       
 
    def fix_srms(self,path='srm:\/\/lofar-srm.fz-juelich.de:8443'):
        for key in self.srms:
            self.srms[key]=re.sub("//pnfs","/pnfs",self.srms[key])
            if "poznan" in self.srms[key]:
                self.srms[key]=re.sub("//lofar","/lofar",self.srms[key])
            self.srms[key]=re.sub(path,'',self.srms[key].split()[0])

 
