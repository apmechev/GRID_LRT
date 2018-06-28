import sys
import re
from collections import deque
from math import ceil
import logging
import subprocess


class srmlist(list):
    """
    The srmlist class is an extension of Python lists that can hold a list of
    srm links to data on GRID Storage (LOFAR Archive, Intermediate Storage, etc).

    In addition to the regular list capabilities, it also has internal checks for the
    location and the OBSID of the data. When a new item is appended, these checks are
    done automatically. Checking OBSID is an optional argument set to True by default.
    """

    def __init__(self, checkOBSID=True, link=None):
        super(srmlist, self).__init__()
        self.lta_location = None
        self.obsid = None
        self.checkobsid = checkOBSID
        if link:
            self.append(link)

    def check_location(self, item):
        tmp_loc = ""
        if isinstance(item, str):
            tmp_loc = self.check_str_location(item)
        elif isinstance(item, srmlist):
            for i in item:
                tmp_loc = self.check_str_location(i)
        return tmp_loc

    def check_str_location(self, item):
        loc = ''
        if 'grid.sara.nl' in item:
            loc = 'sara'
        if 'fz-juelich.de' in item:
            loc = 'juelich'
        if 'lofar.psnc.pl' in item:
            loc = 'poznan'
        return loc

    def stringify_item(self, item):
        if isinstance(item, str):
            link = item.strip('\n')
            link = item.strip('\r')
        elif isinstance(item, srmlist):
            link = "".join(str(v) for v in item)
        else:
            return ""
        return link

    def check_obsid(self, item):
        link = self.stringify_item(item)
        tmp_obsid = re.search('L[0-9]*',
                              link).group(0)
        if not self.obsid:
            self.obsid = tmp_obsid
        if self.checkobsid and tmp_obsid != self.obsid:
            raise AttributeError("Different OBSID than previous items")

    def append(self, item):
        if not item or item == "":
            return
        self.check_obsid(item)
        tmp_loc = self.check_location(item)
        item = self.trim_spaces(self.stringify_item(item))
        if not self.lta_location:
            self.lta_location = tmp_loc
        elif self.lta_location != tmp_loc:
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
            return re.sub("gsiftp://dcachepool12.fz-juelich.de:2811",
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
                          "gsiftp://dcachepool12.fz-juelich.de:2811", item)
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

    def gsi_links(self):
        """
        Returns a generator which can be iterated over, this generator will return
        a set of gsiftp:// links which can be used with globus-url-copy and uberftp
        """
        queue = deque(self)
        while queue:
            item = queue.pop()
            if item:
                yield self.gsi_replace(item)

    def http_links(self):
        """
        Returns a generator that can be used to generate http:// links that can be downloaded
        using wget
        """
        queue = deque(self)
        while queue:
            item = queue.pop()
            if item:
                yield self.http_replace(item)

    def gfal_links(self):
        """
        Returns a generator that can be used to generate links that can be staged/stated with gfal
        """
        queue = deque(self)
        while queue:
            item = queue.pop()
            if item:
                yield self.gfal_replace(item)

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
    srml = srmlist()
    for i in count_files_uberftp(gsiftpdir):
        srml.append(i)
    return srml

def count_files_uberftp(directory):
    logging.info(directory)
    f_list = subprocess.Popen(['uberftp', '-ls', directory],
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out = f_list.communicate()
    if out[1] != '':
        logging.warning("srmls failed to find a directory!! ")
        return 0
    if 'lofsksp' not in out[0]:
        logging.warning("no link found in folder!, returning 0 files")
        return 0
    file_list = [directory+"/"+str(i.split()[-1])
                 for i in out[0].strip().split("\r\n")]
    return file_list

