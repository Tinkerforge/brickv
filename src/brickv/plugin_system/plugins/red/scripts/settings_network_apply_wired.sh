#!/bin/sh

/usr/sbin/service wicd restart
/usr/sbin/wicd --wired -n0 -x
/usr/sbin/wicd --wired -n0 -c
