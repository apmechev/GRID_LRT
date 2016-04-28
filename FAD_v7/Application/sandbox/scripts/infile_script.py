#!/bin/python
import sys

def main(parsetfile,inMS):
	print "Running Parsetscript infile.py"	
	with open(parsetfile,'rb') as pfile:
		lines=[]
		for line in pfile:
			if line.split()[0]=="msin":
				lines.append("msin                    = "+inMS+'\n')
				print "replaced ",inMS, " in\n", line
			elif line.split()[0]=="msout":
				lines.append("msout                   = "+inMS+'.fa\n')
				print "replaced ",inMS, ".fa in\n", line
			else:
				lines.append(line)
	with open(parsetfile,'wb') as pfile:
		for line in lines:
			pfile.write(line)
	

def msinmsout(parsetfile,inMS):
        print "Adding appropriate MS-filenames"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="msin":
                                lines.append("msin                    = "+inMS+'\n')
                                print "replaced ",inMS, " in\n", line
                        elif line.split()[0]=="msout":
                                lines.append("msout                   = "+inMS+'.fa\n')
                                print "replaced ",inMS, ".fa in\n", line
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)




if __name__ == "__main__":
   print "adding ", sys.argv[2], " to ",sys.argv[1]
   main(sys.argv[1],sys.argv[2])
