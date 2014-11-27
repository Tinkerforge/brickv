#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
itype = unicode(argv[2])

if itype == 'wireless':
    cmd_wireless = "/sbin/ifconfig "+iname+" up; "+"/usr/bin/wicd-cli --wireless -x; /etc/init.d/wicd force-reload"
    ps = subprocess.Popen(cmd_wireless, shell=True)
    comm = ps.communicate()
    if cmd_disconnect_restart.returncode:
        exit(1)
elif itype == 'wired':
    cmd_wired = "/sbin/ifconfig "+iname+" up; "+"/usr/bin/wicd-cli --wired -x; \
    /etc/init.d/wicd force-reload; /usr/bin/wicd-cli --wired -c"
    ps = subprocess.Popen(cmd_wired, shell=True)
    comm = ps.communicate()
    if cmd_disconnect_restart.returncode:
        exit(1)
