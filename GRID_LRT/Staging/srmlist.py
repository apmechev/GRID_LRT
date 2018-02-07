import sys
import re
import os
import subprocess
#from GRID_LRT.Staging import surl_chunks
import GRID_LRT.Staging.stage_all_LTA as stage_all
#import GRID_LRT.Staging.state_all as state_all
import GRID_LRT.Staging.stager_access as sa
from collections import deque
import re
from math import ceil
import types

import pdb
import warnings


class srmlist(list):
    """
    The srmlist class is an extension of Python lists that can hold a list of
    srm links to data on GRID Storage (LOFAR Archive, Intermediate Storage, etc).

    In addition to the regular list capabilities, it also has internal checks for the
    location and the OBSID of the data. When a new item is appended, these checks are 
    done automatically. Checking OBSID is an optional argument set to True by default.  
    """
    def __init__(self,checkOBSID=True,link=None):
        self.LTA_location=None
        self.OBSID=None
        self.checkOBSID=checkOBSID
        if link:
            self.append(link)

    def check_location(self,item):
        tmp_loc=""
        if type(item) ==str:
            tmp_loc = self.check_str_location(item)
        elif type(item) == srmlist:
            for i in item:
                tmp_loc = self.check_str_location(i)
        return tmp_loc

    def check_str_location(self,item):
        loc=''
        if 'grid.sara.nl' in item: loc='sara'
        if 'fz-juelich.de' in item: loc='juelich'
        if 'lofar.psnc.pl' in item: loc='poznan'
        return loc

    def stringify_item(self,item):
        if type(item) == str:
            link=item.strip('\n')
            link=item.strip('\r')
        elif type(item) == srmlist :
            link="".join(str(v) for v in item)
        else:
            return ""
        return link

    def check_OBSID(self,item):
        link=self.stringify_item(item)
        tmp_OBSID=re.search('L[0-9][0-9][0-9][0-9][0-9][0-9]',
                link).group(0)
        if not self.OBSID:
            self.OBSID=tmp_OBSID
        if self.checkOBSID and tmp_OBSID!=self.OBSID:
            raise AttributeError("Different OBSID than previous items")

    def append(self, item):
        if item == None or item == "":
            return
        self.check_OBSID(item)
        tmp_loc=self.check_location(item)
        item=self.trim_spaces(self.stringify_item(item))
        if not self.LTA_location:
            self.LTA_location=tmp_loc
        elif self.LTA_location!=tmp_loc:
            raise AttributeError("Appended srm link not the same location as previous links!")
        if item in self:
            return # don't add duplicate srms
        super(srmlist, self).append(item)  #append the item to itself (the list)

    def trim_spaces(self,item):
        """Sometimes there are two fields in the incoming list. Only take the first
        as long as it's fromatted properly
        """
        item=re.sub('//pnfs','/pnfs',"".join(item))
        if self.LTA_location=='poznan':
            item=re.sub('//lofar','/lofar',"".join(item))
        if " " in item:
            for potential_link in item.split(" "):
                if 'srm://' in potential_link:
                    return potential_link
        else:
            return item

    def gfal_replace(self,item):
        """
        For each item, it creates a valid link for the gfal staging scripts
        """
        if('srm://') in item:
            return(re.sub('8443','8443/srm/managerv2?SFN=',item))

    def gsi_replace(self,item):
        if self.LTA_location=='sara': return re.sub('srm://srm.grid.sara.nl:8443',
                                             'gsiftp://gridftp.grid.sara.nl:2811',
                                            item)
        if self.LTA_location=='juelich': return re.sub("srm://lofar-srm.fz-juelich.de:8443","gsiftp://dcachepool12.fz-juelich.de:2811",item)
        if self.LTA_location=='poznan': return re.sub("srm://lta-head.lofar.psnc.pl:8443",
                                                    "gsiftp://gridftp.lofar.psnc.pl:2811",
                                            item)

    def http_replace(self,item):
        if self.LTA_location=='sara': return re.sub('srm://',
                        'https://lofar-download.grid.sara.nl/lofigrid/SRMFifoGet.py?surl=srm://'
                        ,item)
        if self.LTA_location=='juelich': return re.sub(
                    "srm://",
                    "https://lofar-download.fz-juelich.de/webserver-lofar/SRMFifoGet.py?surl=srm://",
                    item)
        if self.LTA_location=='poznan': return re.sub("srm://",
                "https://lta-download.lofar.psnc.pl/lofigrid/SRMFifoGet.py?surl=srm://",item)

    def gsi_links(self):
        """
        Returns a generator which can be iterated over, this generator will return
        a set of gsiftp:// links which can be used with globus-url-copy and uberftp
        """
        q = deque(self)
        while q:
            x = q.pop()
            if x:
                yield self.gsi_replace(x)

    def http_links(self):
        """
        Returns a generator that can be used to generate http:// links that can be downloaded
        using wget
        """
        q = deque(self)
        while q:
            x = q.pop()
            if x:
                yield self.http_replace(x)
    def gfal_links(self):
        """
        Returns a generator that can be used to generate links that can be staged/stated with gfal
        """
        q = deque(self)
        while q:
            x = q.pop()
            if x:
                yield self.gfal_replace(x)


    def sbn_dict(self,pref="SB",suff="_"):
        """
        Returns a generator that creates a pair of SBN and link. Can be used to create dictionaries
        """
        srmdict = {}
        for i in self:
            m = None
            surl=srmlist()
            surl.append(i)
            m = re.search(pref+'(.+?)'+suff,i)
            yield m.group(1),surl



def slice_dicts(srmdict,slice_size=10):
    """
    Returns a dict of lists that hold 10 SBNs (by default). 
    Missing Subbands are treated as empty spaces, if you miss SB009, 
    the list will include  9 items from SB000 to SB008, and next will start at SB010"""
    srmdict=dict(srmdict)

    keys=sorted(srmdict.keys())
    start=int(keys[0])
    sliced={}
    for chunk in range(0,int(ceil(len(keys)/float(slice_size)))):
        chunk_name=format(start+chunk*slice_size,'03')
        sliced[chunk_name]=srmlist()
        for i in range(slice_size):
            if format(start+chunk*slice_size+i,'03') in srmdict.keys():
                sliced[chunk_name].append(srmdict[format(start+chunk*slice_size+i,'03')])
    return sliced


