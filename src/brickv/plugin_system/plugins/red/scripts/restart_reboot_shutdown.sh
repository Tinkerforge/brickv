#!/bin/sh

if [ $# -eq 0 ]
then
    echo "No arguments supplied"
    exit 1

elif [ $1 -eq 0 ]
then
    /etc/init.d/brickd restart

elif [ $1 -eq 1 ]
then
    init 6
#   reboot

elif [ $1 -eq 2 ]
then
    halt

else
    echo "Wrong argument supplied"
    exit 1
fi
