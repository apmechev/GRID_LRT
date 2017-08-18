
function setup_sara_dir(){
rm -rf /dev/shm/* 2>/dev/null

#TODO: Make this block just a git pull?

cp *py $1
cp -r couchdb/ $1
cp -r catalogs $1

cp srm.txt $1 #this is a fallthrough by taking the srm from the token not from the sandbox!
cp -r ddf-pipeline/ $1

cp -r $PWD/tcollector $1
cp parset.cfg $1
rm -rf catalogs/

cd ${RUNDIR}
touch pipeline_status

}

function setup_run_dir(){
 case "$( hostname -f )" in
    *sara*) RUNDIR=`mktemp -d -p $TMPDIR`; setup_sara_dir ${RUNDIR} ;;
    *leiden*) setup_leiden_dir ;;
    node[0-9]*) setup_herts_dir;;
    *) echo "Can't find host in list of supported clusters"; exit 12;;
 esac
}

