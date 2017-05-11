from GRID_LRT.LRTs import fields as fields_LRT
import sys,math,subprocess


def initialize_from_file(OBSIDS_file,line,time_avg=4,freq_avg=4):
    '''Initializes the field object from a file
        by default it sets parameters to 4chan/SB and 4sec resolution
    '''
    lines=[]
    with open(OBSIDS_file,'r') as params:
        for linex in params:
            lines.append(linex.split(','))
    field_values=lines[int(line)]
    targ_OBSID=field_values[1]
    targ_freq=int(field_values[3])/freq_avg
    targ_time=time_avg/int(math.floor(float(field_values[4])))
    cal_freq=int(field_values[8])/freq_avg
    cal_time=time_avg/int(math.floor(float(field_values[9])))
    flags='[ '+field_values[12].replace(" "," , ").replace('\n',' ')+" ]"
    try:
        fieldname=field_values[11]
    except IndexError:
        fieldname=""
    f1=fields_LRT.Field("field_"+fieldname+"_"+str(targ_OBSID))
    f1.initialize("L"+str(targ_OBSID),(cal_time,targ_time),(cal_freq,targ_freq),flags)
    print "Initialized the Field Object:"
    print "OBSIDS for the field are "
    print f1.OBSIDs
    print "srmfiles for the field are " 
    print f1.srms
    return f1



def run_field(f_obj,cal_thresh=0.05):
    '''Queues up the steps inside a field object and launches them one after the other
    '''
    s1=fields_LRT.Stage_step("Stage_targ_init")
    s2=fields_LRT.Stage_step("Stage_cal")
    s3=fields_LRT.Stage_step("Stage_targ_full")

    p1=fields_LRT.pref_Step("pref_cal1")
    p2=fields_LRT.pref_Step("pref_cal2")
    p3=fields_LRT.pref_Step("pref_targ1")
    p4=fields_LRT.pref_Step("pref_targ2")



    f_obj.add_step(s1)
    f_obj.add_step(s2)
    f_obj.add_step(p1)
    f_obj.add_step(p2)
    f_obj.add_step(s3)
    f_obj.add_step(p3)
    f_obj.add_step(p4)

    s1.start(f_obj.srms['targ'][0],threshold=1.) #just stages target and doesn't wait
    
    calfile=subprocess.Popen(['uberftp','-ls','gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/cal_sols/'+f_obj.OBSIDs['cal']+"_solutions.tar"],stdout=subprocess.PIPE)
    cal_results=calfile.communicate()[0] #Find whether the calibrator has been run before 
    print "cal resunts are"+cal_results
    if cal_results=="":
        s2.start(f_obj.srms['cal'][0],threshold=0) #stages and waits for the calibrator 
        p1.start(f_obj.srms['cal'],f_obj.parsets['cal1'],f_obj.OBSIDs['cal'],f_obj.name,args=['-n','1','-t','config/tokens/pref_cal1.cfg','-s','config/sandboxes/pref_cal1.cfg','-j','remote-prefactor-cal1.jdl'])
        p2.start(f_obj.srms['cal'],f_obj.parsets['cal2'],f_obj.OBSIDs['cal'],f_obj.name,args=['-n','244','-t','config/tokens/pref_cal2.cfg','-s','config/sandboxes/pref_cal2.cfg','-j','remote-prefactor-cal2.jdl'],prev_step=p1)

    else:
        s2.progress=1
        p2.progress=1
	p1.progress=1

    s3.start(f_obj.srms['targ'][0],threshold=cal_thresh)#really waits for the target to be staged fully
    s3.start_time=s1.start_time #staging started with s1, gives realistic staging length 
    p3.start(f_obj.srms['targ'],f_obj.parsets['targ'],f_obj.OBSIDs['targ'],f_obj.name,args=['-n','1','-t','config/tokens/pref_targ1.cfg','-s','config/sandboxes/pref_targ1.cfg'],prev_step=p2,calobsid=f_obj.OBSIDs['cal'])      
    p4.start(f_obj.srms['targ'],f_obj.parsets['targ2'],f_obj.OBSIDs['targ'],f_obj.name,args=['-n','10','-t','config/tokens/pref_targ2.cfg','-s','config/sandboxes/pref_targ2.cfg','-j','remote-prefactor-targ2.jdl'],prev_step=p2,calobsid=f_obj.OBSIDs['cal'])



if __name__ == "__main__":
    f1=initialize_from_file(sys.argv[1],sys.argv[2],time_avg=8,freq_avg=2)
    run_field(f1,cal_thresh=0.05)
