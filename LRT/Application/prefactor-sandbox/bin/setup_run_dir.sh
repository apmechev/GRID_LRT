



function setup_run_dir(){

cp $PWD/prefactor.tar $1
#TODO: Make this block just a git pull?
cp download_srms.py $1
cp update*py $1
cp wait_*py $1
cp -r couchdb/ $1
mkdir $1/piechart
cp -r $PWD/piechart/* $1/piechart

cp srm.txt $1 #this is a fallthrough by taking the srm from the token not from the sandbox!

cp ${PARSET} $1
cp -r $PWD/openTSDB_tcollector $1
cp pipeline.cfg $1
cd ${RUNDIR}

log "untarring Prefactor"
tar -xf prefactor.tar

}
