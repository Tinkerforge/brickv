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

dict_status = {'status'     : None,
               'interface'  : None,
               'ip'         : None,
               'subnet_mask': None,
               'gateway'    : None,
               'dns'        : None}

dict_configuration = {'modem'       : None,
                      'dial'        : None,
                      'apn'         : None,
                      'username'    : None,
                      'password'    : None,
                      'sim_card_pin': None}

try:
    if ACTION == 'GET_STATUS':
        sys.stdout.write(json.dumps(dict_status))

    elif ACTION == 'REFRESH':
        p = subprocess.Popen(['/usr/bin/lsusb', '-v'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        p_out_str = p.communicate()[0]

        if p.returncode != 0:
            exit(1)

        if not p_out_str:
            exit(1)

        list_modem = []

        for line in p_out_str.splitlines():
            if not line.startswith('Bus '):
                continue

            entry = line.split(': ')[1].split('ID ')[1].split(' ', 1)
            vid_pid = entry[0]
            name = entry[1]
            
            dict_modem = {'vid_pid' : vid_pid,
                           'name': name}
            
            list_modem.append(dict_modem)

        dict_configuration['modem'] = list_modem

        sys.stdout.write(json.dumps(dict_configuration))

    elif ACTION == 'CONNECT':
        sys.stdout.write(json.dumps(True))

    else:
        exit(1)

except:
    exit(1)
