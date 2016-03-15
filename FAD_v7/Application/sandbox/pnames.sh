#!/bin/bash
# rips out process names for each cachegrind file

touch cmds
for i in CACHEgrind*; do sed -n '4p' $i >> cmds; done
