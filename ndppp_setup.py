<<<<<<< HEAD
from GRID_LRT import sandbox
from GRID_LRT.Staging import srmlist
from GRID_LRT import Token
import os

sandbox_cfg='config/sandboxes/ndppp_cal.cfg'
token_cfg='config/tokens/ndppp_cal.cfg'
srm_file='srm_leah.txt'

s=sandbox.Sandbox()
s.parseconfig(sandbox_cfg)
s.create_SBX_folder()
s.enter_SBX_folder()

s.copy_base_scripts()
#s.load_git_scripts()
s.check_token(token_cfg)
s.zip_SBX()
s.upload_SBX()
s.cleanup()

srm=srmlist.srm_manager()
srm.file_load(srm_file)
_=srm.state()
d=srm.make_sbndict_from_file(srm_file)
OBSID=srm.OBSID

uname=os.environ["PICAS_USR"]
pwd=os.environ["PICAS_USR_PWD"]
pdb=os.environ["PICAS_DB"]
th=Token.Token_Handler(t_type="leah_run2",uname=uname,pwd=pwd,dbn=pdb)
#th.add_overview_view()
#th.add_status_views()
_=th.delete_tokens('todo')
#_=th.delete_tokens('locked')
#_=th.delete_tokens('error')
_=th.reset_tokens('error')


ts=Token.TokenSet(th=th,tok_config=token_cfg)
ts.create_dict_tokens(iterable=d,id_append=OBSID,key_name='start_SB',file_upload='srm.txt')
ts.add_keys_to_list("OBSID",OBSID)

th.views.keys()
#_=th.reset_tokens('error')
#_=th.reset_tokens('locked')
#_=th.reset_tokens('error')
#_=th.delete_tokens('todo')
