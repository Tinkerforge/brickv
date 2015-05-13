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

BINARY_SAKIS3G = '/usr/umtskeeper/sakis3g'
BINARY_UMTSKEEPER = '/usr/umtskeeper/umtskeeper'

SPLIT_SEARCH_INTERFACE = 'Interface: '
SPLIT_SEARCH_OPERATOR = 'Operator name: '
SPLIT_SEARCH_IP = 'IP Address: '
SPLIT_SEARCH_SUBNET_MASK = 'Subnet Mask: '
SPLIT_SEARCH_GATEWAY = 'Default route(s): '

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

def get_DNS():
    with open('/etc/resolv.conf', 'r') as rcfh:
        for line in rcfh.readlines():
            line_split = line.split(' ')

            if len(line_split) == 2 and \
               line_split[0] == 'nameserver' and line_split[1] != '':
                    return line_split[1].strip()

try:
    if ACTION == 'GET_STATUS':
        p = subprocess.Popen([BINARY_SAKIS3G, 'info'],
                             stdout = subprocess.PIPE,
                             stderr = subprocess.PIPE)
        p_out_str = p.communicate()[0]
        
        if p.returncode != 0:
            exit(1)
 
        if not p_out_str:
            exit(1)

        if 'Not connected' in p_out_str:
            dict_status['status'] = 'Not connected'
            dict_status['interface'] = None
            dict_status['ip'] = None
            dict_status['subnet_mask'] = None
            dict_status['gateway'] = None
            dict_status['dns'] = get_DNS()
            sys.stdout.write(json.dumps(dict_status))

        else:
            for line in p_out_str.splitlines():
                if SPLIT_SEARCH_OPERATOR in line and len(line.split(SPLIT_SEARCH_OPERATOR)) == 2:
                    dict_status['status'] = 'Connected to ' + line.split(SPLIT_SEARCH_OPERATOR)[1]

                elif SPLIT_SEARCH_INTERFACE in line and len(line.split(SPLIT_SEARCH_INTERFACE)) == 2:
                    dict_status['interface'] = line.split(SPLIT_SEARCH_INTERFACE)[1]
        
                elif SPLIT_SEARCH_IP in line and len(line.split(SPLIT_SEARCH_IP)) == 2:
                    dict_status['ip'] = line.split(SPLIT_SEARCH_IP)[1]
            
                elif SPLIT_SEARCH_SUBNET_MASK in line and len(line.split(SPLIT_SEARCH_SUBNET_MASK)) == 2:
                    dict_status['subnet_mask'] = line.split(SPLIT_SEARCH_SUBNET_MASK)[1]
            
                elif SPLIT_SEARCH_GATEWAY in line and len(line.split(SPLIT_SEARCH_GATEWAY)) == 2:
                    dict_status['gateway'] = line.split(SPLIT_SEARCH_GATEWAY)[1]
        
            dict_status['dns'] = get_DNS() 
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
