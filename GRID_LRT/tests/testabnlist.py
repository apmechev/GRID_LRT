import srmlist
Srm_obj=srmlist.Srm_manager("L544905")
Srm_obj.stride=10
Srm_obj.file_load("../../SKSP/srmfiles/srm544905.txt")
abnlist=Srm_obj.make_srmdict_from_tokens("pref_field_544905",10)

