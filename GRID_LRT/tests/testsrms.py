import srmlist
l1=srmlist.Srm_manager(OBSID="L544905")
l1.file_load(filename='../../SKSP/srmfiles/srm544905.txt')
print l1.srms['111']
o=l1.state()
l1.stage()
