import sys
import re
from collections import deque
from math import ceil
import logging
import subprocess
from GRID_LRT.Staging import surl_chunks
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

    @property
    def LTA_location(self):
        if len(self)>0:
            return self.check_str_location(self[0])
    
    def check_str_location(self, item):
        """searches the item for an FQDN and returns the location
        of the data using the list below. Returns the data location or None"""
        for fqdn in GSI_FQDNs:
            if fqdn in item:
                return GSI_FQDNs[fqdn] 

    def stringify_item(self, item):
        if isinstance(item, str):
            link = item.strip('\n')
            link = item.strip('\r')
        elif isinstance(item, srmlist):
            link = "".join(str(v) for v in item)
        else:
            return ""
        return link

    def _check_obsid(self, item):
        link = self.stringify_item(item)
        tmp_obsid = re.search('L[0-9][0-9]*',
                              link).group(0)
        if not self.obsid:
            self.obsid = tmp_obsid
        if self.checkobsid and tmp_obsid != self.obsid:
            raise AttributeError("Different OBSID than previous items")

    def append(self, item):
        if not item or item == "":
            return
        if self.checkobsid:
            self._check_obsid(item)
        tmp_loc = self.check_link_location(item)
        item = self.trim_spaces(self.stringify_item(item))
        if not self.lta_location:
            self.lta_location = tmp_loc
        elif self.lta_location != tmp_loc  and self._check_location :
            raise AttributeError(
                "Appended srm link not the same location as previous links!")
        if item in self:
            return  # don't add duplicate srms
        # append the item to itself (the list)
        super(srmlist, self).append(item)

    def trim_spaces(self, item):
        """Sometimes there are two fields in the incoming list. Only take the first
        as long as it's fromatted properly
        """
        item = re.sub('//pnfs', '/pnfs', "".join(item))
        if self.lta_location == 'poznan':
            item = re.sub('//lofar', '/lofar', "".join(item))
        if " " in item:
            for potential_link in item.split(" "):
                if 'srm://' in potential_link:
                    return potential_link
        else:
            return item

    def gfal_replace(self, item):
        """
        For each item, it creates a valid link for the gfal staging scripts
        """
        if 'srm://' in item:
            return re.sub(':8443', ':8443/srm/managerv2?SFN=', item)
        elif 'gsiftp://' in item:
            return self.srm_replace(item)

    def srm_replace(self, item):
        if self.lta_location == 'sara':
            return re.sub('gsiftp://gridftp.grid.sara.nl:2811',
                          'srm://srm.grid.sara.nl:8443',
                          item)
        if self.lta_location == 'juelich':
            return re.sub("gsiftp://lofar-gridftp.fz-juelich.de:2811",
                          "srm://lofar-srm.fz-juelich.de:8443",
                          item)
        if self.lta_location == 'poznan':
            return re.sub("gsiftp://gridftp.lofar.psnc.pl:2811",
                          "srm://lta-head.lofar.psnc.pl:8443",
                          item)

    def gsi_replace(self, item):
        if self.lta_location == 'sara':
            return re.sub('srm://srm.grid.sara.nl:8443',
                          'gsiftp://gridftp.grid.sara.nl:2811',
                          item)
        if self.lta_location == 'juelich':
            return re.sub("srm://lofar-srm.fz-juelich.de:8443",
                    "gsiftp://lofar-gridftp.fz-juelich.de:2811", item)
        if self.lta_location == 'poznan':
            return re.sub("srm://lta-head.lofar.psnc.pl:8443",
                          "gsiftp://gridftp.lofar.psnc.pl:2811",
                          item)

    def http_replace(self, item):
        if self.lta_location == 'sara':
            return re.sub('srm://',
                          'https://lofar-download.grid.sara.nl/lofigrid/SRMFifoGet.py?surl=srm://',
                          item)
        if self.lta_location == 'juelich':
            return re.sub(
                "srm://",
                "https://lofar-download.fz-juelich.de/webserver-lofar/SRMFifoGet.py?surl=srm://",
                item)
        if self.lta_location == 'poznan':
            return re.sub("srm://",
                          "https://lta-download.lofar.psnc.pl/lofigrid/SRMFifoGet.py?surl=srm://",
                          item)

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
        print(th.t_type)
        v=th.db.view(th.t_type+"/"+"done")
        sbns=[]
        for x in v:
            if th.db[x["id"]]["pipeline"]=='pref_targ1':
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
                print("Sorry. could not get OBSID")
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
            print("\033[31mOBSID not found in SRM file!\033[0m")
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

    def sbn_dict(self, pref="SB", suff="_"):
        """
        Returns a generator that creates a pair of SBN and link. Can be used to create dictionaries
        """
        for i in self:
            match = None
            surl = srmlist()
            surl.append(i)
            match = re.search(pref+'(.+?)'+suff, i)
            try:
                yield match.group(1), surl
            except AttributeError as exc:
                sys.stderr.write("Are you using pref='SB' and suff='_'"+
                                 "to match ...SB000_... ?")
                raise exc


def slice_dicts(srmdict, slice_size=10):
    """
    Returns a dict of lists that hold 10 SBNs (by default).
    Missing Subbands are treated as empty spaces, if you miss SB009,
    the list will include  9 items from SB000 to SB008, and next will start at SB010"""
    srmdict = dict(srmdict)

    keys = sorted(srmdict.keys())
    start = int(keys[0])
    sliced = {}
    for chunk in range(0, 1 + int(ceil((int(keys[-1])-int(keys[0]))/float(slice_size)))):
        chunk_name = format(start+chunk*slice_size, '03')
        sliced[chunk_name] = srmlist()
        for i in range(slice_size):
            if format(start+chunk*slice_size+i, '03') in srmdict.keys():
                sliced[chunk_name].append(
                    srmdict[format(start+chunk*slice_size+i, '03')])
    sliced = dict((k, v) for k, v in sliced.items() if v) #Removing empty items
    return sliced

def make_srmlist_from_gsiftpdir(gsiftpdir):
    from GRID_LRT.storage import gsifile
    srml = srmlist()
    grid_dir = gsifile.GSIFile(gsiftpdir)
    for i in [f.loc for f in grid_dir.list_dir()]:
        srml.append(i)
    return srml

def count_files_uberftp(directory):
    from GRID_LRT.storage import gsifile
    grid_dir = gsifile.GSIFile(directory)
    return [f.location for f in grid_dir.list_dir()]
