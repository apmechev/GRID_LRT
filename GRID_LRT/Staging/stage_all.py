#!/usr/bin/env python

""" Staging script using the gfal API

# ===================================================================== #
# author: Ron Trompert <ron.trompert@surfsara.nl>	--  SURFsara    #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: python stage_all.py                                                #
# description:                                                          #
#	Stage the files listed in "files". The paths should have the 	#
#	'/pnfs/...' format. The pin lifetime is set with the value 	#
#	'srmv2_desiredpintime'. 						#
# ===================================================================== #
"""

from __future__ import print_function

import re
import sys
import gfal2 as gfal  # pylint: disable=import-error
from GRID_LRT.Staging import srmlist as srmlist_module


##>>> ctx = gfal2.creat_context()
#>>> (status, token) = ctx.bring_online(surl, 60, 60, True)


class LTA_Stager(object):
    """Stager that handles a file/srmlist and stages it. It can wait
    for the staging to complete"""

    def __init__(self,filename=None, srmlist=None):
        if srmlist and isinstance(srmlist,srmlist_module.srmlist):
            self.srmlist = srmlist
        else:
            self.srmlist = srmlist_module.srmlist()
        pass

    def load_from_filemane(self, filename):
        for i in open(filename):
            self.srmlist.append(i.strip('\r\n'))



def main(filename):
    """Given a filename, it stages the srms
    and prints 'staged' if completed
    """
    file_loc = location(filename)
    replace_string, match = replace(file_loc)
    srmfile = open(filename, 'r')
    urls = srmfile.readlines()
    srmfile.close()
    return process(urls, replace_string, match)


def state_dict(srm_dict):
    """Decides on the location of the data using
    a srm link and creates a dictionary
    """
    locs_options = ['s', 'j', 'p']

    line = srm_dict.itervalues().next()
    file_loc = [locs_options[i] for i in range(len(locs_options)) if [
        "sara" in line, "juelich" in line,
        "sara" not in line and "juelich" not in line][i] is True][0]
    replace_string, match = replace(file_loc)

    urls = []
    for _, value in srm_dict.iteritems():
        urls.append(value)
    return process(urls, replace_string, match)


def location(filename):
    """Gives the location of the entire filename
    """
    locs_options = ['s', 'j', 'p']
    with open(filename, 'r') as srmfile:
        line = srmfile.readline()

    file_loc = [locs_options[i] for i in range(len(locs_options)) if [
        "sara" in line, "juelich" in line, "sara" not in line and "juelich" not in line][i] is True]
    return file_loc[0]


def replace(file_loc):
    """Replaces the srmlink with the manager used to stage data"""
    if file_loc == 'p':
        match = re.compile('/lofar')
        repl_string = "srm://lta-head.lofar.psnc.pl:8443/srm/managerv2?SFN=/lofar"
        print("Staging in Poznan")
    else:
        match = re.compile('/pnfs')
        if file_loc == 'j':
            repl_string = "srm://lofar-srm.fz-juelich.de:8443/srm/managerv2?SFN=/pnfs/"
            print("Staging in Juleich")
        elif file_loc == 's':
            repl_string = "srm://srm.grid.sara.nl:8443/srm/managerv2?SFN=/pnfs"
            print("files are on SARA")
        else:
            sys.exit()
    return repl_string, match

def stage_srm(surl, pintime, timeout, asynch=True):
    context = gfal.creat_context()
    (errors, token) = context.bring_online(surl, pintime, timeout, asynch)
    return errors, token

def process(urls, repl_string, match):
    """Main function that invokes
    gfal on all the srms to stage them"""
    surls = []
    for url in urls:
        surls.append(url.strip())

    err, tok = stage_srm(surls, 24*3600, 3600)

    req = {}
    # Set the timeout to 24 hours
    # gfal_set_timeout_srm  Sets  the  SRM  timeout, used when doing an asyn-
    # chronous SRM request. The request will be aborted if it is still queued
    # after 24 hours.
    # Set the time that the file stays pinned on disk for a week (604800sec)

    print("staging request sent")
    return  err, tok 

if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        sys.exit(main('files'))
