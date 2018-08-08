# ===================================================================== #
# author: Ron Trompert <ron.trompert@surfsara.nl>	--  SURFsara    #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: python stage.py                                                #
# description:                                                          #
#	Stage the files listed in "files". The paths should have the 	#
#	'/pnfs/...' format. The pin lifetime is set with the value 	#
#	'srmv2_desiredpintime'. 					#
# ===================================================================== #

#!/usr/bin/env python

#import pythonpath
#import gfal2 as gfal
import re
import sys
from GRID_LRT.Staging import stager_access 


def strip(item):
    return item.strip()


def process_surl_line(line):
    """ Used to drop empty lines and to
        take the first argument of the srmfile (the srm:// link)
    """

    if " " in line:
        line = line.split(" ")[0]
    if line == "/n":
        return None 
    return line


def main(filename, test=False):
    file_loc = location(filename)
    rs, m = replace(file_loc)
    with open(filename, 'r') as f:
        urls = f.readlines()
    return process(urls, rs, m, test)


def return_srmlist(filename):
    file_loc = location(filename)
    regex, match = replace(file_loc)
    _file = open(filename, 'r')
    urls = _file.readlines()
    _file.close()
    surls = []
    for url in urls:
        url = process_surl_line(url)
        if "managerv2?SFN" in url:
            surls.append(match.sub(regex, strip(u)))
        elif url:
            surls.append(url)
    return surls


def state_dict(srm_dict):
    locs_options = ['s', 'j', 'p']

    line = srm_dict.itervalues().next()
    file_loc = [locs_options[i] for i in range(len(locs_options)) if [
        "sara" in line, "juelich" in line, not "sara" in line and not "juelich" in line][i] == True][0]
    regex, match = replace(file_loc)

    urls = []
    for key, value in srm_dict.iteritems():
        urls.append(value)
    return process(urls, regex, match)


def location(filename):
    locs_options = ['s', 'j', 'p']
    with open(filename, 'r') as _file:
        line = _file.readline()

        file_loc = [locs_options[i] for i in range(len(locs_options)) if [
            "sara" in line, "juelich" in line, not "sara" in line and not "juelich" in line][i] == True]
    return file_loc[0]


def replace(file_loc):
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


def process(urls, repl_string, match, test=False):
    surls = []
    for url in urls:
        if not 'srm' in url:
            surls.append(match.sub(repl_string, strip(url)))
        else:
            surls.append(strip(url))
    req = {}
    print("Setting up "+str(len(surls))+" srms to stage")
    if test:
        return
    stageid = stager_access.stage(surls)

    print("staged with stageID ", stageid)
    return stageid


def get_stage_status(stageid):
    return stager_access.get_status(int(stageid))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        sys.exit(main(sys.argv[1]))
    else:
        sys.exit(main('files'))
