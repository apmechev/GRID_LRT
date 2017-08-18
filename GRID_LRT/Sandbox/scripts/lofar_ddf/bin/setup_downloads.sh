


#This function takes the Pipeline type as $1 and executes the appropriate dl setup sub_function 
function setup_downloads(){

echo "setup_dl: Setting up downloads"
globus-url-copy >/dev/null 2>&1
if [[ $? ==  127 ]]
 then 
    echo "setup_dl: globus-url-copy doesn't exist. ";exit 13
fi

if [ ! -z $( echo $1 | grep ddf_image2 ) ]
 then
  setup_image2
fi
touch temp_mslist.txt

echo "setup_dl: inal srms to download"
cat srm.txt
}


function setup_image2(){

  echo ""
  echo "setup_dl: downloading intermediate results "
  echo "result location:"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/ddf/ddf_image1/${OBSID}
  echo "setup_dl: Setting download of subbands in OBSID ${OBSID}"
  globus-url-copy gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/ddf/ddf_image1/${OBSID}/step1.tar

}



