# ===================================================================== #
# author: Ron Trompert <ron.trompert@surfsara.nl>	--  SURFsara    #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara	#
#                                                            	        #
# usage: python state.py						#
# description:                                                       	#
#	Display the status of each file listed in "files". The paths 	#
#	should have the '/pnfs/...' format. Script output:		#
#		ONLINE: means that the file is only on disk		#
#		NEARLINE: means that the file in only on tape		#
#		ONLINE_AND_NEARLINE: means that the file is on disk	#
#				     and tape				#
#                                                                       #
# UPDATED                                                               #
# - 02/06/2016 JBRO created POZNAN version                              #
# ===================================================================== #

# SARA
# srm://srm.grid.sara.nl:8443/pnfs/grid.sara.nl/data/lofar/ops/projects/lc2_038/229585/L229585_SB000_uv.dppp.MS_65198c92.tar
# sed -e "s/srm:\/\/srm.grid.sara.nl:8443//" datasets/L229585/srmlist > files
# /pnfs/grid.sara.nl/data/lofar/ops/projects/lc2_038/229585/L229585_SB000_uv.dppp.MS_65198c92.tar

# JUELICH
# srm://lofar-srm.fz-juelich.de:8443/pnfs/fz-juelich.de/data/lofar/ops/projects/lc4_034/403972/L403972_SB133_uv.dppp.MS_e2218c21.tar
# sed -e "s/srm:\/\/lofar-srm.fz-juelich.de:8443//" datasets/L403972/srmlist > files
# /pnfs/fz-juelich.de/data/lofar/ops/projects/lc4_034/403972/L403972_SB133_uv.dppp.MS_e2218c21.tar

# POZNAN (does not work!)
# srm://lta-head.lofar.psnc.pl:8443/lofar/ops/projects/lc5_007/441220/L441220_SB029_uv.dppp.MS_8b1adae4.tar
# sed -e "s/srm:\/\/lta-head.lofar.psnc.pl:8443//" datasets/L441220/srmlist > files
# /lofar/ops/projects/lc5_007/441220/L441220_SB029_uv.dppp.MS_8b1adae4.tar


#!/usr/bin/env python

import pythonpath
import gfal
import time
import re
import sys
from string import strip
def main(filename):
	#m=re.compile('/pnfs') #SARA/JUELICH
	m=re.compile('/lofar') #POZNAN
	nf=100
	
	f=open(filename,'r')
	urls=f.readlines()
	f.close()
	
	surls=[]
	for u in urls:
	#    surls.append(m.sub('srm://srm.grid.sara.nl:8443/srm/managerv2?SFN=/pnfs',strip(u)))
	##    surls.append(m.sub('srm://dcache-lofar.fz-juelich.de:8443/srm/managerv2?SFN=/pnfs/',strip(u)))
	#    surls.append(m.sub('srm://lofar-srm.fz-juelich.de:8443/srm/managerv2?SFN=/pnfs/',strip(u)))
	    surls.append(m.sub('srm://lta-head.lofar.psnc.pl:8443/srm/managerv2?SFN=/lofar',strip(u)))
	
	#print "SURLS: ", surls
	#sys.exit()
	
	mx=len(surls)
	locality=[]	
	#FORMAT SARA
	#surls=['srm://srm.grid.sara.nl:8443/srm/managerv2?SFN=/pnfs/grid.sara.nl/data/lofar/ops/projects/lc2_038/229585/L229585_SB000_uv.dppp.MS_65198c92.tar']
	#
	#FORMAT POZNAN
	#surls=['srm://lta-head.lofar.psnc.pl:8443/srm/managerv2?SFN=/lofar/ops/projects/lc5_007/441220/L441220_SB029_uv.dppp.MS_8b1adae4.tar']
	
	i=0
	while i<mx:
	    req={}
	    mxi=min(i+nf,mx)
	    s=surls[i:mxi]
	    #print "s: ", s
	    req.update({'surls':s})
	    req.update({'setype':'srmv2'})
	    req.update({'no_bdii_check':1})
	    req.update({'srmv2_lslevels':1})
	    req.update({'protocols':['gsiftp']})
	    a,b,c=gfal.gfal_init(req)
	    a,b,c=gfal.gfal_ls(b)
	    a,b,c=gfal.gfal_get_results(b)
	    #print "a: ", a
	    #print "b: ", b
	    #print "c: ", c
            for j in range(0,len(c)):
               if c[j]['locality']=='NEARLINE':
                        colour="\033[31m"
               else:
                        colour="\033[32m"
               print c[j]['surl']+" "+colour+c[j]['locality']+"\033[0m"
               locality.append([c[j]['surl'],c[j]['locality']])
	    i=i+nf
	    time.sleep(1)
	return locality

if __name__=='__main__':
          if len(sys.argv)==2:
                  sys.exit(main(sys.argv[1]))
          else:
                  sys.exit(main('files'))

