#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import subprocess
from sys import argv

if len(argv) < 3:
    exit (1)

iname = unicode(argv[1])
itype = unicode(argv[2])

if itype == 'wireless':
    cmd_deactivate_wireless = "/sbin/ifconfig "+iname+" down"
    ps = subprocess.Popen(cmd_deactivate_wireless, shell=True)
    comm = ps.communicate()
if itype == 'wired':
    cmd_deactivate_wired = "/sbin/ifconfig "+iname+" down"
    ps = subprocess.Popen(cmd_deactivate_wired, shell=True)
    comm = ps.communicate()
