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
import time
import re
import sys
strip = lambda x:x.strip()
from GRID_LRT.Staging import stager_access as sa
import pdb


def process_surl_line(line):
    """ Used to drop empty lines and to 
        take the first argument of the srmfile (the srm:// link)
    """

    if " " in line:
        line=line.split(" ")[0]
    if line =="/n":
        return
    return line


def main(filename):
    file_loc=location(filename)
    rs,m=replace(file_loc)
    with open(filename,'r') as f:
        urls=f.readlines()
    return (process(urls,rs,m))

def return_srmlist(filename):
    file_loc=location(filename)
    rs,m=replace(file_loc)
    f=open(filename,'r')
    urls=f.readlines()
    f.close()
    surls=[]
    for u in urls:
        u=process_surl_line(u)
        if "managerv2?SFN" in u:
            surls.append(m.sub(rs,strip(u)))
        else:
            surls.append(u)
    return surls

def state_dict(srm_dict):
    locs_options=['s','j','p']

    line=srm_dict.itervalues().next()
    file_loc=[locs_options[i] for i in range(len(locs_options)) if ["sara" in line,"juelich" in line, not "sara" in line and not "juelich" in line][i] ==True][0]
    rs,m=replace(file_loc)

    urls=[]
    for key, value in srm_dict.iteritems():
        urls.append(value)
    return (process(urls,rs,m))




def location(filename):
    locs_options=['s','j','p']
    with open(filename,'r') as f:
        line=f.readline()

        file_loc=[locs_options[i] for i in range(len(locs_options)) if ["sara" in line,"juelich" in line, not "sara" in line and not "juelich" in line][i] ==True]
    return file_loc[0]

def replace(file_loc):
    if file_loc=='p':
        m=re.compile('/lofar')
        repl_string="srm://lta-head.lofar.psnc.pl:8443/srm/managerv2?SFN=/lofar"
        print("Staging in Poznan")
    else:
        m=re.compile('/pnfs')
        if file_loc=='j':
            repl_string="srm://lofar-srm.fz-juelich.de:8443/srm/managerv2?SFN=/pnfs/"
            print("Staging in Juleich")
        elif file_loc=='s':
            repl_string="srm://srm.grid.sara.nl:8443/srm/managerv2?SFN=/pnfs"
            print("files are on SARA")
        else:
            sys.exit()
    return repl_string,m



def process(urls,repl_string,m):
    surls=[]
    for u in urls:
        if not 'srm' in u:
            surls.append(m.sub(repl_string,strip(u)))
        else:
            surls.append(strip(u))
    req={}
    print("Setting up "+str(len(surls))+" srms to stage")
    stageID=sa.stage(surls)

    print("staged with stageID ", stageID)
    return stageID

def get_stage_status(stageID):
    return sa.get_status(int(stageID))


if __name__=='__main__':
    if len(sys.argv)==2:
        sys.exit(main(sys.argv[1]))
    else:
        sys.exit(main('files'))

