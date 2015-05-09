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

dict_configuration = {'apn'             : None,
                      'username'        : None,
                      'password'        : None,
                      'phone'           : None,
                      'sim_card_pin'    : None,
                      'use_provider_dns': None}

def detect_device():
    with open(os.devnull, 'w') as nfh_w:
        child = subprocess.Popen(['/bin/mktemp', '-t', 'tmp.XXX'], stdout = subprocess.PIPE, stderr = nfh_w)
        _tmp_file = ''
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

    elif ACTION == 'REFRESH':
        if not os.path.exists(FILE_CONIG_WVDIAL):
            sys.stdout.write(json.dumps(dict_configuration))

        else:
            with open(FILE_CONIG_WVDIAL, 'r') as wcfh_r:
                config = ConfigParser.ConfigParser()
                config.readfp(wcfh_r)
    
                dict_configuration['apn'] = None
                dict_configuration['username'] = None
                dict_configuration['password'] = None
                dict_configuration['phone'] = None
                dict_configuration['sim_card_pin'] = None
                dict_configuration['use_provider_dns'] = None
    
                for section in config.sections():
                    for option in config.options(section):
                        if option == 'Username':
                            dict_configuration['username'] = config.get(section, 'Username')
                        elif option ==  'username':
                            dict_configuration['username'] = config.get(section, 'username')
        
                        if option == 'Password':
                            dict_configuration['password'] = config.get(section, 'Password')
                        elif option == 'password':
                            dict_configuration['password'] = config.get(section, 'password')
        
                        if option == 'Phone':
                            dict_configuration['phone'] = config.get(section, 'Phone')
                        elif option == 'phone':
                            dict_configuration['phone'] = config.get(section, 'phone')
                        
                        if option == 'Auto DNS':
                            if config.get(section, 'Auto DNS') == 'yes' or \
                               config.get(section, 'Auto DNS') == 'Yes' or \
                               config.get(section, 'Auto DNS') == 'YES' or \
                               config.get(section, 'Auto DNS') == '1':
                                    dict_configuration['use_provider_dns'] = True
                            else:
                                dict_configuration['use_provider_dns'] = False
                        elif option == 'auto DNS':
                            if config.get(section, 'auto DNS') == 'yes' or \
                               config.get(section, 'auto DNS') == 'Yes' or \
                               config.get(section, 'auto DNS') == 'YES' or \
                               config.get(section, 'auto DNS') == '1':
                                    dict_configuration['use_provider_dns'] = True
                            else:
                                dict_configuration['use_provider_dns'] = False

            sys.stdout.write(json.dumps(dict_configuration))

    elif ACTION == 'CONNECT':
        pass

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
            value = 'AT+CPIN="' + sys.argv[2] + '","' + sys.argv[3] + '"'

            config.set('Dialer puk', option, value)

        if not config:
            exit(1)

        with open(tmp_file, 'w') as tfh_w:
            config.write(tfh_w)

        child = subprocess.Popen(['/usr/bin/wvdial', '-C', tmp_file, 'puk'],
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE)

        # Not checking returncode because the tool returns error code as the tool looks for
        # username, password and phone number but they are not needed for PUK operations
        child_output = ''
        child_output = child.communicate()[1]

        if child_output and 'Sending: AT+CPIN="{0}","{1}"\nOK'.format(sys.argv[2], sys.argv[3]) not in child_output:
            exit(1)

    else:
        exit(1)

except:
    exit(1)
