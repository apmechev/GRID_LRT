#!/usr/bin/env python 
"""Module to parse list of surls and create a dictionary with chunks
of custom number of links (parameter stride, default=1)
"""
import os
import re
import sys
import glob

__author__ = "Raymond Oonk, Alexandar Mechev"
__credits__ = ["Raymond Oonk", "Alexandar Mechev", "Natalie Danezi",
                 "Timothy Shimwell"]
__license__ = "GPL 3.0"
__version__ = "0.1.1"
__maintainer__ = "Alexandar Mechev"
__email__ = "apmechev@strw.leidenuniv.nl"
__status__ = "Production"

# -------------------------------------------------
# TO RUN: python gsurl.py infile


# parameters set by user when starting
#

def make_list_of_surls(infile,stride):
    """Makes a dictionary of surls given an input file and surls per item
    
    """
    f=open(infile, 'r')
    stridecount=0
    srmdict={}
    for line in f:
        if stridecount%int(stride) != 0:
            stridecount+=1
            continue
        stridecount+=1
        if not line in ['\n','\r\n','\r']: #skips empty lines
            line=re.sub('//pnfs','/pnfs',line)
            surl=line.split()[0]
            tmp1=line.split('SB')[1]
            sbn=tmp1.split('_')[0]
            srmdict[(int(sbn),int(sbn))]=surl
            #srmdict[sbn]=surl

    print('created srmDICT from ', infile)
    return srmdict


def main(infile,stride=1):
        """main() method for legacy compatibility 
        """
	#infile          = str(sys.argv[1])
	outsrm		= 'srmlist'
	outsbl		= 'subbandlist'
	
	print( 'infile: ', infile)
	
	# START PROGRAM
	print( 'START GET SURL:', infile)
	
	#open in file
	f=open(infile, 'r')
	
	#clear and open outfile
	os.system('rm -f '+outsrm)
	os.system('rm -f '+outsbl)
	srm=open(outsrm, 'w')
	sbl=open(outsbl, 'w')
	stridecount=0
	#read lines
	for line in f:
	    if stridecount%int(stride) != 0:
	    	stridecount+=1
		continue
	    #surl=line
	    stridecount+=1
	    if not line in ['\n','\r\n','\r']:
		line=re.sub('//pnfs','/pnfs',line)
	    	surl=line.split()[0]
	    	#print surl
	    	srm.write('%s\n' % surl)
	
	    #tmp1=line.split(' ')[1]
	    	tmp1=line.split('SB')[1]
	    	sbn=tmp1.split('_')[0]
	    	#print sbn
	    	sbl.write('%s\n' % sbn)
	
	f.close()
	srm.close()
	sbl.close()
	
	print('created srmlist from ', infile)
	print('done')

if __name__=='__main__':
    if len(sys.argv)==3:
	sys.exit(main(sys.argv[1],sys.argv[2]))
    else:
         sys.exit(main(sys.argv[1]),1)
