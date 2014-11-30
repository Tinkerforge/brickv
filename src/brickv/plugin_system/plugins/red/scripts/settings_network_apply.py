#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
itype = unicode(argv[2])

if itype == 'wireless':
    netidx = unicode(argv[3])
    cmd_wireless = '/sbin/ifconfig '+iname+' up &&\
                    /usr/sbin/service wicd restart &&\
                    /bin/sleep 5 && /usr/bin/wicd-cli --wireless -c -n'+netidx+' && :'
    cmd_wireless_code = os.system(cmd_wireless)
    if cmd_wireless_code:
        exit (1)

elif itype == 'wired':
    cmd_wired = '/sbin/ifconfig '+iname+' up &&\
                 /usr/sbin/service wicd restart &&\
                 /bin/sleep 5 && /usr/bin/wicd-cli --wired -c -n0 && :'
    cmd_wired_code = os.system(cmd_wired)
    if cmd_wired_code:
        exit (1)
else:
    exit (1)
