
function setup_sara_dir(){

cp *parset $1
cp -r  $PWD/prefactor/ $1
#TODO: Make this block just a git pull?
cp download_srms.py $1
cp *py $1
cp -r couchdb/ $1
mkdir $1/piechart
cp -r $PWD/piechart/* $1/piechart

cp srm.txt $1 #this is a fallthrough by taking the srm from the token not from the sandbox!

cp ${PARSET} $1
cp -r $PWD/tcollector $1
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

