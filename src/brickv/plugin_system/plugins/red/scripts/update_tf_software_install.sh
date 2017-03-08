#!/bin/sh

if [ $# -ne 1 ]; then
    exit 1
fi

# Directory path where the updates are stored.
echo $1

exit 0
