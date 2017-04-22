#!/bin/bash

function make_pie(){

xmlfile=$( find . -name "*statistics.xml" 2>/dev/null)
cp piechart/autopie.py .
./autopie.py ${xmlfile} PIE_${OBSID}.png
cp $! ${WORKDIR}

}








function make_plots(){


echo ""


}
