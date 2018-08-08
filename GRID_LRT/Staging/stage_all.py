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


def process(urls, repl_string, match):
    """Main function that invokes
    gfal on all the srms to stage them"""
    surls = []
    for url in urls:
        surls.append(match.sub(repl_string, url.strip()))

    req = {}
    # Set the timeout to 24 hours
    # gfal_set_timeout_srm  Sets  the  SRM  timeout, used when doing an asyn-
    # chronous SRM request. The request will be aborted if it is still queued
    # after 24 hours.
    gfal.gfal_set_timeout_srm(86400)

    req.update({'surls': surls})
    req.update({'setype': 'srmv2'})
    req.update({'no_bdii_check': 1})
    req.update({'protocols': ['gsiftp']})

    # Set the time that the file stays pinned on disk for a week (604800sec)
    req.update({'srmv2_desiredpintime': 604800})

    returncode, obj, err = gfal.gfal_init(req)
    if returncode != 0:
        sys.stderr.write(err+'\n')
        sys.exit(1)

    returncode, obj, err = gfal.gfal_prestage(obj)
    if returncode != 0:
        sys.stderr.write(err+'\n')
        sys.exit(1)
    del req
    print("staged")


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        sys.exit(main('files'))
