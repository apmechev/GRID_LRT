<<<<<<< HEAD
from GRID_LRT import sandbox
from GRID_LRT.Staging import srmlist
from GRID_LRT import Token
import os
import sys 

sandbox_cfg='config/sandboxes/ddf_image2.cfg'
token_cfg='config/tokens/ddf_image2.cfg'
OBSID=sys.argv[1]

s=sandbox.Sandbox()
s.parseconfig(sandbox_cfg)
s.create_SBX_folder()
s.enter_SBX_folder()

s.copy_base_scripts()
s.load_git_scripts()
s.check_token(token_cfg)
s.zip_SBX()
s.upload_SBX()
s.cleanup()

srm=srmlist.srm_manager(stride=844)
#srm.file_load(srm_file)
#_=srm.state()
d=srm.make_sbndict_from_gsidir("gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/distrib/SKSP/"+str(OBSID))
#OBSID=srm.OBSID
#OBSID="L570741"
#d={1:""}

uname=os.environ["PICAS_USR"]
pwd=os.environ["PICAS_USR_PWD"]
pdb=os.environ["PICAS_DB"]
th=Token.Token_Handler(t_type="ddf_"+OBSID,uname=uname,pwd=pwd,dbn=pdb)
th.add_overview_view()
th.add_status_views()
_=th.delete_tokens('todo')
_=th.delete_tokens('locked')
_=th.delete_tokens('error')
_=th.reset_tokens('error')


ts=Token.TokenSet(th=th,tok_config=token_cfg)
ts.create_dict_tokens(iterable=d,id_append=OBSID,file_upload='srm.txt')
ts.add_keys_to_list("OBSID",OBSID)
ts.add_attach_to_list('parsets/image2.cfg',name='parset.cfg')
#ts.add_attach_to_list('srm.txt',name='srm.txt')

th.views.keys()

