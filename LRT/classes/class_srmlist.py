import sys
import re


class Srmlist(object):


    def __init__(self,OBSID="",filename="",stride=1):
        """Initializes the srmlist object. The stride is how many tokens to make
            stride=1 makes token for each link, stride 10 groups by 10, etc
            The self.srms dictionary is what is used later by the default_LRT
            to make the tokens and possibly to rearrange the links by real frequency
        """
        self.OBSID=OBSID
        self.filename=filename
        self.stride=stride
        self.srms={} #A dictionary of {SBN,surl}


    def file_load(self,filename,OBSID=""):
        """Loads a list of srms from a file by searching the file for 
            1. The OBSID class is initiated
            2. The OBSID given by this function
            3. The first OBSID encountered in the file
            After, the script only loads the lines that contain the OBSID
            into the dict srms
        """
        self.filename=filename
        if self.OBSID=="" and OBSID!="":
            self.OBSID=OBSID
        self.check_OBSID()
        
 
        sys.path.append('LRT/gsurl')
        import gsurl_v3
        self.srms=gsurl_v3.make_list_of_surls(self.filename,self.stride) 

        f1=open(self.filename,'r').read()
        if "fz-juelich.de" in f1:
            self.fix_srms('srm:\/\/lofar-srm.fz-juelich.de:8443')
        elif "srm.grid.sara.nl" in f1:
            self.fix_srms('srm:\/\/srm.grid.sara.nl:8443')
        elif "lofar.psnc.pl" in f1:
            self.fix_srms('srm:\/\/lta-head.lofar.psnc.pl:8443')
        

    def get_freq_from_token(self,token):
        pass

 
    def check_OBSID(self):
        """If the OBSID is empty, it takes the first OBSID from the file
            Otherwise it checks if the OBSID exists in the file
            If more than one OBSIDs in the file, it makes a new one and
            sets self.filename to that
        """
        if self.OBSID=="":
            with open(self.filename,'r') as txtfile:
                line=txtfile.readline()
                self.OBSID='L'+str(re.search("L(.+?)_",line).group(1))
            if self.OBSID=="":
                print "Sorry. could not get OBSID"
                raise KeyError
        found=False

        #Tests if only one OBSID in file 
        with open(self.filename,'rt') as f:
            for line in f:
                if self.OBSID in line:
                    found=True
                else:
                    lines=open(self.filename,'r').readlines()
                    with open(self.OBSID+".txt",'w') as file1:
                        [file1.write(x) for x in lines if self.OBSID in x]
                    self.filename=self.OBSID+".txt"
        if not found:
            print "\033[31mOBSID not found in SRM file!\033[0m"
            sys.exit()


    def state(self): 
        sys.path.append('../Staging/')
        import state_all
        self.states=state_all.state_dict(self.srms)

    def stage(self):
        sys.path.append('../Staging/')
        import stage_all
        self.stages=stage_all.state_dict(self.srms)


    def fix_srms(self,path='srm:\/\/lofar-srm.fz-juelich.de:8443'):
        for key in self.srms:
            self.srms[key]=re.sub("//pnfs","/pnfs",self.srms[key])
            if "poznan" in self.srms[key]:
                self.srms[key]=re.sub("//lofar","/lofar",self.srms[key])
            self.srms[key]=re.sub(path,'',self.srms[key].split()[0])

 
