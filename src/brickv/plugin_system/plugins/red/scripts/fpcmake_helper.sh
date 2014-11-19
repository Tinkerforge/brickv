#!/bin/sh -e

export PATH=/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin
export FPCDIR=/usr/lib/fpc/`ls /usr/lib/fpc/ | grep -E [0-9].[0-9].[0-9] | head -n1`

cd $1
shift
fpcmake
make $@
