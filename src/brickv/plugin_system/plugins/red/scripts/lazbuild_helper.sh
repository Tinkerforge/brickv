#!/bin/sh -e

export FPCDIR=/usr/lib/fpc/default

cd $1
shift
lazbuild $@ *.lpi
