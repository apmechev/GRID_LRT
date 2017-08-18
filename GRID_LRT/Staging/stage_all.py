# ===================================================================== #
# author: Ron Trompert <ron.trompert@surfsara.nl>	--  SURFsara    #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara    #
#                                                                       #
# usage: python stage.py                                                #
# description:                                                          #
#	Stage the files listed in "files". The paths should have the 	#
#	'/pnfs/...' format. The pin lifetime is set with the value 	#
#	'srmv2_desiredpintime'. 						#
# ===================================================================== #

#!/usr/bin/env python

import pythonpath
import gfal2 as gfal
import time
import re
import sys
from string import strip


def main(filename):
        file_loc=location(filename)
        rs,m=replace(file_loc)
        f=open(filename,'r')
        urls=f.readlines()
        f.close()
        return (process(urls,rs,m))

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
	    surls.append(m.sub(repl_string,strip(u)))
	
	req={}
	# Set the timeout to 24 hours
	# gfal_set_timeout_srm  Sets  the  SRM  timeout, used when doing an asyn-
	# chronous SRM request. The request will be aborted if it is still queued
	# after 24 hours.
	gfal.gfal_set_timeout_srm(86400)
	
	req.update({'surls':surls})
	req.update({'setype':'srmv2'})
	req.update({'no_bdii_check':1})
	req.update({'protocols':['gsiftp']})
	
	#Set the time that the file stays pinned on disk for a week (604800sec)
	req.update({'srmv2_desiredpintime':604800})
	
	returncode,object,err=gfal.gfal_init(req)
	if returncode != 0:
	        sys.stderr.write(err+'\n')
	        sys.exit(1)
	
	returncode,object,err=gfal.gfal_prestage(object)
	if returncode != 0:
	    sys.stderr.write(err+'\n')
	    sys.exit(1)
	del req
        print "staged"	


if __name__=='__main__':
        if len(sys.argv)==2:
                sys.exit(main(sys.argv[1]))
        else:
                sys.exit(main('files'))

