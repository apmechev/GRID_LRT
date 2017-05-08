#!/bin/bash

function tarlogs(){
# find . -iname "*statistics.xml" -exec tar -rvf profile.tar {} \;
# find . -name "*png" -exec tar -rvf profile.tar {} \;
# tar --append --file=profile.tar output

 case "${PIPELINE}" in
    ndppp_cal) echo "" ;;
    ndppp_targ) tar_logs_targ ;;
    *) echo "Can't find PIPELINE type "; exit 12;;
 esac


}


function tar_logs_targ(){




}
