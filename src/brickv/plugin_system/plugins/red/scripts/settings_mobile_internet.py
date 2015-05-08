#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import tempfile
import netifaces
import subprocess
import ConfigParser

if len(sys.argv) < 2:
    exit (1)

ACTION = sys.argv[1]
FILE_CONIG_WVDIAL = '/etc/tf_wvdial.conf'

dict_status = {'status': None,
               'interface': None,
               'ip': None,
               'subnet_mask': None,
               'gateway': None,
               'dns': None}

dict_configuration = {'apn': None,
                      'username': None,
                      'password': None,
                      'number': None,
                      'sim_card_pin': None,
                      'use_provider_dns': None}

def detect_device():
    with open(os.devnull, 'w') as nfh_w:
        child = subprocess.Popen(['/bin/mktemp', '-t', 'tmp.XXX'], stdout = subprocess.PIPE)
        _tmp_file = child.communicate()[0]

        if _tmp_file:
            tmp_file = _tmp_file.strip()

        if child.returncode:
            return False, None

        child = subprocess.Popen(['/usr/bin/wvdialconf', tmp_file], stdout = nfh_w, stderr = nfh_w)
        child.communicate()

        if child.returncode:
            return False, None

        return True, tmp_file

try:
    if ACTION == 'GET_STATUS':
        pass
        #if not detect_device():
            #exit(2)
    elif ACTION == 'REFRESH':
        pass
        #if not detect_device():
            #exit(2)
    elif ACTION == 'CONNECT':
        pass
        #if not detect_device():
            #exit(2)
    elif ACTION == 'PUK':
        if len(sys.argv) < 4:
            exit(1)

        result, tmp_file = detect_device()

        if not result:
            exit(2)

        config = None

        with open(tmp_file, 'r') as tfh_r:
            config = ConfigParser.ConfigParser()
            config.readfp(tfh_r)

            config.add_section('Dialer puk')

            option = 'Init3'
            value = 'AT+CPIN="'+sys.argv[2]+'","'+sys.argv[3]+'"'

            config.set('Dialer puk', option, value)

        if not config:
            exit(1)

        with open(tmp_file, 'w') as tfh_w:
            config.write(tfh_w)

        # Now execute the actual PUK command
    else:
        exit(1)

except:
    exit(1)
