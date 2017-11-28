


#This function takes the Pipeline type as $1 and executes the appropriate dl setup sub_function 
function setup_downloads(){

echo "setup_dl: Setting up downloads"
globus-url-copy >/dev/null 2>&1
if [[ $? ==  127 ]]
 then 
    echo "setup_dl: globus-url-copy doesn't exist. ";exit 13
fi
touch srm.txt

if [ ! -z $( echo $1 | grep init_sub ) ]
 then
  setup_init_sub
fi

if [ ! -z $( echo $1 | grep targ2 ) ] 
 then
  setup_targ2   
fi


if [ ! -z $( echo $1 | grep cal2 ) ]
 then
  setup_cal2
fi

echo "setup_dl: inal srms to download"
cat srm.txt
}




function setup_init_sub(){

  echo ""
  echo "setup_dl: processing INITIAL-SUBTRACT Parset ${PARSET}"
  echo ""
  echo "setup_dl: Setting download of subbands in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_cal1/${OBSID} |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "setup_dl: found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  rm -rf srm*txt
  grep $STARTSB gsiftps_init.txt > srm-final.txt
}

function setup_cal2(){
  echo ""

  echo ""
  echo "setup_dl: Setting download of instruments in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_cal1/${OBSID}/  |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "setup_dl: found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  #rm -rf srm*txt
  #grep $STARTSB gsiftps_init.txt > srm-final.txt
  mv gsiftps_init.txt srm.txt
}

function setup_targ2(){

  echo ""
  echo "setup_dl: Doing GSMCal for ${OBSID}"
  echo ""
  echo "setup_dl: Setting download of subbands in OBSID ${OBSID}"
  uberftp -ls -r gsiftp://gridftp.grid.sara.nl:2811/pnfs/grid.sara.nl/data/lofar/user/sksp/pipelines/SKSP/pref_targ1/${OBSID}/ |awk '{print "srm://srm.grid.sara.nl:8443"$NF}' > gsiftps_init.txt
  echo "setup_dl: found these gsiftps associated with ${OBSID}"
  cat gsiftps_init.txt
  echo ""
  #rm -rf srm*txt
  #grep $STARTSB gsiftps_init.txt > srm-final.txt
  cp srm.txt srm-final.txt
  sed -i "s?num_SBs_per_group.*=?num_SBs_per_group    = 10?g" *parset 
}
