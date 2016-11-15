


#This function takes the Pipeline type as $1 and executes the appropriate dl setup sub_function 
function setup_downloads(){

echo "Setting up downloads"

if [ ! -z $( echo $1 | grep init_sub ) ]
 then
 setup_init_sub
fi

if [ ! -z $( echo $1 | grep targ2 ) ] 
 then
 setup_targ2   
fi

echo "Final srms to download"
cat srm-final.txt
}


function setup_init_sub(){

  echo ""
  echo "processing INITIAL-SUBTRACT Parset ${PARSET}"
  echo ""
  echo "Setting download of subbands in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/ |grep $OBSID |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  rm -rf srm*txt
  grep $STARTSB gsiftps_init.txt > srm-final.txt
}


function setup_targ2(){

  echo ""
  echo "Doing GSMCal for ${OBSID}"
  echo ""
  echo "Setting download of subbands in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/spectroscopy-migrated/prefactor/SKSP/${OBSID}/t1* |grep $OBSID |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  #rm -rf srm*txt
  #grep $STARTSB gsiftps_init.txt > srm-final.txt
  cp srm.txt srm-final.txt
  sed -i "s?num_SBs_per_group.*=?num_SBs_per_group    = 10?g" *parset 


}
