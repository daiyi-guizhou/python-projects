#!/bin/bash
if ping -c 1 $1 >/dev/null 2>&1
then 
    # echo True
    echo 1
else 
    # echo Flase
    echo 0
fi