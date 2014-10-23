#!/bin/sh

if [ "$#" -gt 0 ]
then
    /usr/bin/wicd-cli --wireless -l
else
    /usr/bin/wicd-cli --wireless -Sl
fi
