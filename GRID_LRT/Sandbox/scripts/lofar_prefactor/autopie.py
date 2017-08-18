#!/usr/bin/env python
# coding: utf-8
#     autopie.py is a combination of three scripts to Parse LOFAR statstics and 
#     make a pie chart 
#
#     usage: ./autopie.py <path/to/statistics.xml> <name_of_chart.png>
#
#     make_sqlite.py: Parse LOFAR statistics files and write to an sqlite database
#     Copyright (C) 2016 
#     ASTRON (Netherlands Institute for Radio Astronomy) <http://www.astron.nl/>
#     P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
# 
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
# 
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
# 
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
# 
"""Script to parse LOFAR statistics files to an sqlite database that can 
later be used to plot performance statistics on the pipeline run."""
import multiprocessing as mp
from xml.dom import minidom
import os
import time

def xmlparse(xmlfile):
    """ 
    Open and parse a LOFAR statistics xml file.
    xmlfile: path of the file to parse
    return: tuple of elements.
    order of elements: date, stack_name, task_name, duration, job list 
    """
    xmldoc = minidom.parse("%s"%(xmlfile))
    # Retrieve xml nodes
    print "parsing "+xmlfile
    date = os.path.basename(os.path.dirname(xmlfile))
    stack = xmldoc.childNodes[0]
    stack_name = stack.getAttribute('Name')
    
    ret_list = list()
    res_list = list()
    for task in stack.childNodes:
        task_name = task.nodeName
        task_duration = task.getAttribute('duration')
    if task_duration:
            task_item = (date, stack_name, task_name, task_duration, [])
        task_res = (date, stack_name, task_name, [])
            for node in task.childNodes:
                for job in node.childNodes:
                    job_duration = job.getAttribute('duration')
                    job_host = job.getAttribute('job_host')
                    job_id = job.getAttribute('job_id')
                    job_item = (job_duration, job_host, job_id)
                    task_item[-1].append(job_item)
            jobdata=[]
            for res in job.childNodes:
            #assert only 1 in res!
            if len(res.childNodes)>1:
                print "Needs to iterate over res as well"
            proc=res.childNodes[0]
            timedata=[]
            for point in proc.childNodes:
                timepoint=[]
                timepoint.append(int(point.getAttribute("timestamp")))
                                timepoint.append(int(point.getAttribute("read_bytes")))
                                timepoint.append(int(point.getAttribute("write_bytes")))
                timedata.append(timepoint)
            jobdata.append(timedata)
                task_res[-1].append(jobdata)
            ret_list.append(task_item)
        res_list.append(task_res) 
    
    return ret_list,res_list



#     simple_stats.py: Derive basic statistics from parsed statistics database.
#     Copyright (C) 2016
#     ASTRON (Netherlands Institute for Radio Astronomy) <http://www.astron.nl/>
#     P.O.Box 2, 7990 AA Dwingeloo, The Netherlands
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

#import sqlite3
from math import sqrt


def simple_stats():
        r=xmlparse(dargs['input_file'])[0]
#       print "--"
    results1=[]
    for i in range(len(r)):
        rsum=0.0
        for j in r[i][4]:
            rsum+=float(j[0])
        if rsum==0.0:
            rsum=float(r[i][3])
        results1.append((r[i][2],float(r[i][3]),float(r[i][3]),rsum*rsum))
#       print results1
    ns=[]
    for n in results1:
        name = n[0]
        nsum = n[1]
        nave = n[2]
        try:
        nstdev = sqrt(n[3] - n[2]**2)
        except:
        nstdev=0.0 #make more elegant!
        ns.append([name, nsum, nave, nstdev])
    return ns




import sys
import os




####
##
## Makes a pie-chart using a given statistics.xml file.
####
dargs={}#A global dictionary of variables so that there's no 'return blah,blah,[...],blah' and so I don't acutally write a class (why use a class when a dictionary is enough anyways?)

def parse_args(args):
    """
    The script will go through all xml files in the input files set and write the data in those to an sqlite database. 
    """
    dargs["imagefile"]="pie.png"
    for arg in args:
         if ("xml" in arg[:]):
                 dargs['input_file']=arg
                 continue
         if ("png" in arg[:]):
         dargs["imagefile"]=arg

    if not os.path.isfile(dargs['input_file']):
    print "the input file is incorrect"
    if os.path.dirname(dargs['input_file'])!="":
        import glob
        xmldir=os.path.dirname(dargs['input_file'])
        xmlfiles=glob.glob(xmldir+'/*xml')
        if len(xmlfiles)>0:
            print "I found "+str(len(xmlfiles))+" xml files, which one should I run?"
            from termios import tcflush, TCIOFLUSH
            for i in range(len(xmlfiles)):
                print "press "+str(i)+" to choose "+ xmlfiles[i]
            userchoice = raw_input().lower()
            if int(userchoice) in range(len(xmlfiles)+1):
                userchoice=int(userchoice)
            else:
                sys.exit()
            dargs['input_file']=xmlfiles[userchoice]
    print "processing "+dargs['input_file']
    f = open('xmlfile','w')
    f.write(dargs['input_file'])
    f.close()
    dargs['outdb'] = "temp_pie.db"
    return

import sys
from string import digits


def process(stats):
        duration_threshold = 0.03
        names=[]
        for line in stats:
            name = line.split()[0]
            name = name.translate(None, digits)
            names.append(name)

        # All iteration numbers are discarded, so duplicates are to be removed
        names = list(set(names))

        # Iterate all operations
        data = list()
        duration_total = 0
        for name in names:
            selection = filter(lambda x: name in x, stats)
            duration = sum(map(lambda x: float(x.split()[1]), selection))
            duration_total += duration
            data.append((name, duration))

        # Process all operations
        data.sort(key=lambda x: x[1], reverse=True)
        duration_misc = 0
        perc=[]
        for operation in data:
            name = operation[0]
            name = name.replace("_", "-")
            duration = operation[1]
            duration_fraction = duration/duration_total
            if duration_fraction > duration_threshold:
#               print "%s/%.3f," % (name, duration_fraction*100)
                perc.append([name,duration_fraction])
            else:
                duration_misc += duration

        # Print duration for misc category
#       print "%s/%.3f" % ("misc", duration_misc/duration_total*100)
        perc.append(['misc',duration_misc/duration_total])
        return perc

def main(args):
    parse_args(args)
    stats=simple_stats()

    flatstats=[str(item[0])+" "+str(item[1])+" "+str(item[2])+" "+str(item[3])+" \n" for item in stats]
    percentages=process(flatstats)
    labels=[]
    values=[]
    for i in range(len(percentages)):
        labels.append(percentages[i][0])
        values.append(percentages[i][1])
    print labels, values
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    my_cmap = matplotlib.cm.get_cmap('Set3')
    my_norm = matplotlib.colors.Normalize(0, 1)
    color_vals = [float(i/float(len(values))) for i in range(len(values))]
    print color_vals
    plt.title("Processing time spent in steps")
    plt.pie(values, labels=labels,colors=my_cmap(my_norm(color_vals)), autopct='%1.1f%%')
    fig = matplotlib.pyplot.gcf()
    #fig.title("Processing time spent in steps")
    #fig.pie(values, labels=labels,colors=my_cmap(my_norm(color_vals)), autopct='%1.1f%%')
    fig.set_size_inches(10.5, 10.5)
    fig.savefig(dargs["imagefile"])
    plt.show()



if __name__ == "__main__":
    main(sys.argv)

