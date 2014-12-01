#!/bin/sh

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

if [ $1 -eq 0 ]
  then
    /etc/init.d/brickd restart
fi

if [ $1 -eq 1 ]
  then
    init 6
#   reboot
fi

if [ $1 -eq 2 ]
  then
    halt
fi
