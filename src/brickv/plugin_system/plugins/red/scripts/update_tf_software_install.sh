#!/bin/sh

if [ $# -ne 2 ]; then
    exit 1
fi

# Name of the update (to figure out how to install it).
echo $1

# Full path of the update.
echo $2

exit 0
