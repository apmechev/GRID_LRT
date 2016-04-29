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
	

def msinmsout(parsetfile,inMS,outMS=""):
        print "Adding appropriate MS-filenames"
	if outMS=="":
		outMS=inMS+".fa"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="msin":
                                lines.append("msin                    = "+inMS+'\n')
                                print "replaced ",inMS, " in ", line.split()[0]
                        elif line.split()[0]=="msout":
                                lines.append("msout                   = "+outMS+'\n')
                                print "replaced ",outMS, " in ", line.split()[0]
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)




def avgtimefreqstep(parsetfile,avg_freq_step,avg_time_step):
        print "Adding Averager time/freq steps"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="avg1.freqstep":
                                lines.append("avg1.freqstep           = "+avg_freq_step+'\n')
                                print "replaced ",avg_freq_step, " in ", line.split()[0]
                        elif line.split()[0]=="avg1.timestep":
                                lines.append("avg1.timestep           = "+avg_time_step+'\n')
                                print "replaced ",avg_time_step, " in ", line.split()[0]
                        elif line.split()[0]=="demixer.freqstep":
                                lines.append("demixer.freqstep        = "+avg_freq_step+'\n')
                                print "replaced ",avg_freq_step, " in ", line.split()[0]
                        elif line.split()[0]=="demixer.timestep":
                                lines.append("demixer.timestep        = "+avg_time_step+'\n')
                                print "replaced ",avg_time_step, " in ", line.split()[0]

                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)

def dmxtimefreqstep(parsetfile,dmx_freq_step,dmx_time_step):
        print "Adding Demixer time/freq steps"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="demixer.demixfreqstep":
                                lines.append("demixer.demixfreqstep   = "+dmx_freq_step+'\n')
                                print "replaced ",dmx_freq_step, " in ", line.split()[0]
                        elif line.split()[0]=="demixer.demixtimestep":
                                lines.append("demixer.demixtimestep   = "+dmx_time_step+'\n')
                                print "replaced ",dmx_time_step, " in ", line.split()[0]
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)




def dmxsources(parsetfile,dmx_src):
        print "Adding Demixer sources"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="demixer.subtractsources":
                                lines.append("demixer.subtractsources = ["+dmx_src+']\n')
                                print "replaced ",dmx_src, " in ", line.split()[0]
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)

def dodmx(parsetfile,do_dmx):
	print do_dmx
	if do_dmx=="False" or do_dmx=="FALSE" or do_dmx=='false':
		return
        with open(parsetfile,'rb') as pfile:
	        print "Turning on demixer"
                lines=[]
                for line in pfile:
                        if line.split()[0]=="steps":
                                lines.append(line.replace("avg1","demixer"))
                                print "replaced ",lines[-1], " instead of ", line
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)



def selectnl(parsetfile,sel_nl):
        if sel_nl=="True" or sel_nl=="TRUE" or sel_nl=="true":
                return
        with open(parsetfile,'rb') as pfile:
                print "Selecting International Stations"
                lines=[]
                for line in pfile:
                        if line.split()[0]=="msin.baseline":
                                lines.append("msin.baseline           = \n")
                                print "replaced ",lines[-1], " instead of ", line
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)

def timesteps(parsetfile,st,en):
        print "Adding timesplit timesteps"
        with open(parsetfile,'rb') as pfile:
                lines=[]
                for line in pfile:
                        if line.split()[0]=="msin":
				lines.append(line)
				lines.append("msin.starttime          = "+st+"\n")
				lines.append("msin.endtime            = "+en+"\n")
				print "Current chunk start/end times are "+st+en 
                        else:
                                lines.append(line)
        with open(parsetfile,'wb') as pfile:
                for line in lines:
                        pfile.write(line)



if __name__ == "__main__":
   print "adding ", sys.argv[2], " to ",sys.argv[1]
   main(sys.argv[1],sys.argv[2])
