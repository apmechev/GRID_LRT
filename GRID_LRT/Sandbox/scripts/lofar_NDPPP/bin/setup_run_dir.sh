
function setup_sara_dir(){


#TODO: Make this block just a git pull?
cp download_srms.py $1
cp *py $1
cp -r couchdb/ $1
cp lp_targ.sh ${RUNDIR}

cp srm.txt $1 #this is a fallthrough by taking the srm from the token not from the sandbox!


cd ${RUNDIR}

}

function setup_run_dir(){
 case "$( hostname -f )" in
    *sara*) RUNDIR=`mktemp -d -p $TMPDIR`; setup_sara_dir ${RUNDIR} ;;
    *leiden*) setup_leiden_dir ;;
    node[0-9]*) setup_herts_dir;;
    *) echo "Can't find host in list of supported clusters"; exit 12;;
 esac
}

