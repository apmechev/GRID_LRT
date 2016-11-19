import sys,os
sys.path.append(os.getcwd()+"/LRT/classes")

import Token

import class_default_LRT as LRT

th=Token.Token_Handler(uname=os.environ["PICAS_USR"],pwd=os.environ["PICAS_USR_PWD"],dbn=os.environ["PICAS_DB"],t_type=sys.argv[1])

num_to_sub=th.reset_tokens("error")
L=LRT.LRT()
L.jdl_file="remote.jdl"
L.t_type=sys.argv[1]
L.OBSID="resub"
L.workdir=os.environ["PWD"]
L.numpernode=1
L.start_jdl(num_to_sub)
