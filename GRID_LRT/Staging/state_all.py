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
# ===================================================================== #

#!/usr/bin/env python

import pythonpath
try:
    import gfal2 as gfal
except ImportError:
    print("GFAL CANNOT BE IMPORTED")
    pass
import sys
from GRID_LRT.Staging.srmlist import srmlist
from GRID_LRT import grid_credentials
import pdb
from collections import Counter


def main(filename, verbose=True):
    """Main function that takes in a file name and returns a list of tuples of 
    filenames and staging statuses. The input file can be both srm:// and gsiftp:// links.

    Args:
        :param filename: The filename holding the links whose have to be checked
        :type filename: str
        :param verbose: A toggle to turn off printing out the status of each file. True by default will print everything out
        :type verbose: bool

    Returns:
        :ret results: A list of tuples containing the file_name and the State

    Usage: 

    >>> from GRID_LRT.Staging import state_all
    >>> filename='/home/apmechev/GRIDTOOLS/GRID_LRT/GRID_LRT/tests/srm_50_sara.txt'
    >>> results=state_all.main(filename)
    >>> results=state_all.main(filename, verbose=False)
    >>> results[0]
    ('L229507_SB150_uv.dppp.MS_f6fc7fc5.tar', 'ONLINE_AND_NEARLINE')

    """
    grid_credentials.grid_credentials_enabled() # Check if credenitals enabled
    s_list=load_file_into_srmlist(filename)
    print("files are at "+s_list.LTA_location)
    results=[]
    for i in s_list.gfal_links():
        results.append(check_status(i,verbose))
    return results

def load_file_into_srmlist(filename):
    """Helper function that loads a file into an srmlist object (will be
    added to the actual srmlist class later)

    """
    s=srmlist()
    for i in open(filename,'r').read().split():
        s.append(i)
    return s

def check_status(surl, verbose=True):
    """ Obtain the status of a file from the given surl.

    Args:
        :param surl: the SURL pointing to the file.
        :type surl: str
        :parame verbose: print the status to the terminal.
        :type verbose: bool

    Returns:
        :(filename, status): a tuple containing the file  and status as 
            stored in the 'user.status' attribute.
    """
    context = gfal.creat_context()
    status = context.getxattr(surl, 'user.status')
    filename = surl.split('/')[-1]
    if status=='ONLINE_AND_NEARLINE' or status=='ONLINE':
        color="\033[32m"
    else :
        color="\033[31m"
    if verbose:
        print('{:s} is {:s}{:s}\033[0m'.format(filename, color,status))
    return (filename, status)

def percent_staged(results):
    """Takes list of tuples of (srm, status) and counts the percentage of files
    that are staged (0->1) and retunrs this percentage as float

    Usage:
    
    >>> from GRID_LRT.Staging import state_all
    >>> filename='/home/apmechev/GRIDTOOLS/GRID_LRT/GRID_LRT/tests/srm_50_sara.txt'
    >>> results=state_all.main(filename, verbose=False)
    >>> state_all.percent_staged(results)

    """
    total_files=len(results)
    counts = Counter(x[1] for x in results)
    staged=counts['ONLINE_AND_NEARLINE']+counts['ONLINE']
    unstaged=counts['NEARLINE']
    print(str(float(staged/total_files)*100)+" percent of files staged")
    return float(staged/total_files)

if __name__ == '__main__':
    surl = sys.argv[1]
    if (surl.lower()).startswith('srm://'):
        # Single file.
        check_status(surl)
    else:
        # Assume a file list.
        check_status_file(surl)
	
