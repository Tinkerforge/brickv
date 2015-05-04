#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import apt
import json
import netifaces
import ConfigParser

if len(sys.argv) < 2:
    exit (1)

cache = apt.Cache()

if not cache['wvdial'].is_installed:
    exit(1)

ACTION = sys.argv[1]
FILE_CONIG_WVDIAL = '/etc/tf_wvdial.conf'
COMMAND_DETECTION = '/usr/bin/wvdialconf /etc/somefile'

try:
    if ACTION == 'GET':
        if os.system():
            exit(1)

    elif ACTION == 'CONNECT':
        pass
    elif ACTION == 'PUK':
        if len(sys.argv) < 4:
            exit(1)
    else:
        exit(1)
except:
    exit(1)
