# ============================================================================================  #
# author: Natalie Danezi <anatoli.danezi@surfsara.nl>   --  SURFsara                            #
# helpdesk: Grid Services <grid.support@surfsara.nl>    --  SURFsara                            #
#                                                                                               #
# usage: ./run_remote_sandbox.sh [picas_db_name] [picas_username] [picas_pwd] [token_type]      #
# description: Get grid tools from github, and launch getOBSID which takes a token of the type  #
#              specified, downloads the appropriate sandbox and executes it                     #
#                                                                                               #
#          apmechev: Modified and frozen to standardize job launching                           #
#          - Sept 2016                                                                          #
#                                                                                               #
# ============================================================================================  #

set -x

#Clones the picas tools repository which interfaces with the token pool
#uses wget if no git

if type git &> /dev/null
then
 git clone https://github.com/apmechev/GRID_picastools.git p_tools_git
 cd p_tools_git
 git checkout testpy3
 cd ../
else  #move this to testpy3
 wget -O master.zip https://github.com/apmechev/GRID_picastools/archive/testpy3.zip 
 unzip master.zip -d p_tools_git/ 
fi

mv p_tools_git/* . 
rm -rf p_tools_git/

echo "Downloaded the test_py3 branch and Launching Token Type $4"


#launches script designed to lock token, download sandbox with 
#token's OBSID and execute the master.sh in the sandbox
python Launch.py  $1 $2 $3 $4 &
wait

ls -l
cat log*


