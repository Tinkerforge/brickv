#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
itype = unicode(argv[2])

if itype == 'wireless':
    netidx = unicode(argv[3])
    cmd_wireless = '/sbin/ifconfig '+iname+' up;/bin/sleep 1;\
                    /usr/bin/wicd-cli --wired -x;/bin/sleep 4;/usr/bin/wicd-cli --wireless -x;/bin/sleep 4;\
                    /usr/sbin/service wicd restart;/bin/sleep 4;/usr/bin/wicd-cli --wireless -c -n'+netidx
    ps_wireless = subprocess.Popen(cmd_wireless, shell=True)
    comm = ps_wireless.communicate()
    if ps_wireless.returncode:
        exit (1)

if itype == 'wired':
    cmd_wired = '/sbin/ifconfig '+iname+' up;/bin/sleep 1;\
                 /usr/bin/wicd-cli --wired -x;/bin/sleep 4;/usr/bin/wicd-cli --wireless -x;/bin/sleep 4;\
                 /usr/sbin/service wicd restart;/bin/sleep 4;/usr/bin/wicd-cli --wired -c -n0'
    ps_wired = subprocess.Popen(cmd_wired, shell=True)
    comm = ps_wired.communicate()
    if ps_wired.returncode:
        exit (1)
