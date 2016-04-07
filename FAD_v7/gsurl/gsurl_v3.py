import os
import re
import sys
import glob

#--------------------------------------------------
# Versioning.
# Original: JBR Oonk (ASTRON/LEIDEN) Dec 2015
#  - v2 added creation subbandlist alongside srmlist
#  - v3 changed to account for for when file:/// is not given
#--------------------------------------------------

# -------------------------------------------------
# TO RUN: python gsurl.py infile


# parameters set by user when starting
#

def main(infile):
	#infile          = str(sys.argv[1])
	outsrm		= 'srmlist'
	outsbl		= 'subbandlist'
	
	print 'infile: ', infile
	
	# START PROGRAM
	print 'START GET SURL:', infile
	
	#open in file
	f=open(infile, 'r')
	
	#clear and open outfile
	os.system('rm -f '+outsrm)
	os.system('rm -f '+outsbl)
	srm=open(outsrm, 'w')
	sbl=open(outsbl, 'w')
	
	#read lines
	for line in f:
	    #surl=line
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
	sbl.close
	
	print 'created srmlist from ', infile
	print 'done'

if __name__=='__main__':
    sys.exit(main(sys.argv[1]))
