#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
itype = unicode(argv[2])

if itype == 'wireless':
    cmd_disconnect_restart = "/sbin/ifconfig "+iname+" down; "+"/usr/bin/wicd-cli --wireless -x; /etc/init.d/wicd force-reload"
    ps = subprocess.Popen(cmd_disconnect_restart, shell=True)
    comm = ps.communicate()
elif itype == 'wired':
    cmd_disconnect_restart_connect = "/sbin/ifconfig "+iname+" down; "+"/usr/bin/wicd-cli --wired -x; \
    /etc/init.d/wicd force-reload; /usr/bin/wicd-cli --wired -c"
    ps = subprocess.Popen(cmd_disconnect_restart_connect, shell=True)
    comm = ps.communicate()
