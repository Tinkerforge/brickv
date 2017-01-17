#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
iname_previous = unicode(argv[2])
itype = unicode(argv[3])

if iname_previous and iname_previous != 'None':
    cmd_ifdown = '/sbin/ifconfig '+iname_previous+' down 2> /dev/null && /bin/sleep 1'
    os.system(cmd_ifdown)

if itype == 'wireless':
    cmd_wireless = '/usr/bin/wicd-cli --wireless -x && /bin/sleep 5 &&\
                    /usr/sbin/service wicd restart && /bin/sleep 8 && :'

    cmd_wireless_code = os.system(cmd_wireless)

    if cmd_wireless_code:
        exit (1)

elif itype == 'wired':
    cmd_wired = '/usr/bin/wicd-cli --wired -x && /bin/sleep 5 &&\
                 /usr/sbin/service wicd restart && /bin/sleep 5 &&\
                 /usr/bin/wicd-cli --wired -c -n0 && :'
    cmd_wired_code = os.system(cmd_wired)
    if cmd_wired_code:
        exit (1)
else:
    exit (1)
