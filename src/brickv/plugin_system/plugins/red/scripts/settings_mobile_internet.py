#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import re
import os
import sys
import json
import netifaces
import subprocess

if len(sys.argv) < 2:
    exit (1)

ACTION = sys.argv[1]

UNIT_SYSTEMD = '''[Unit]
Description=systemd service for Tinkerforge mobile internet

[Service]
Type=Simple
TimeoutStartSec=5
ExecStart=/usr/umtskeeper/umtskeeper --conf /usr/umtskeeper/umtskeeper.conf
TimeoutStopSec=5
ExecStop=/usr/bin/killall -9 pppd

[Install]
WantedBy=multi-user.target
'''

CONFIG_UMTSKEEPER = '''conf['deviceName'] = 'modem_mobile_internet'
conf['sakisSwitches'] = "--nostorage --pppd --nofix --console"
conf['sakisOperators'] = "{0}"
conf['sakisMaxFails'] = 8
conf['sakisFailLockDuration'] = 120
conf['wrongPinDelay'] = 60
conf['DNSprobeDomain'] = 'google.com'
conf['DNSprobeCycle'] = 600
conf['writeStats'] = False
conf['printMsg'] = False
conf['logMsg'] = True
conf['logFile'] = '/var/log/umtskeeper.log'
'''

TAG_CONFIG_SAKIS_OPERATORS = "conf['sakisOperators']"
TAG_PARAM_SIM_PIN = 'SIM_PIN'
TAG_PARAM_DIAL = 'DIAL'
TAG_PARAM_APN = 'APN'
TAG_PARAM_APN_USER = 'APN_USER'
TAG_PARAM_APN_PASS = 'APN_PASS'
TAG_PARAM_USBMODEM = 'USBMODEM'

SERVICE_SYSTEMD_TF_MOBILE_INTERNET = 'tf_mobile_internet.service'
FILE_UNIT_TF_MOBILE_INTERNET = '/etc/systemd/system/' + SERVICE_SYSTEMD_TF_MOBILE_INTERNET
FILE_CONFIG_UMTSKEEPER = '/usr/umtskeeper/umtskeeper.conf'

BINARY_SAKIS3G = '/usr/umtskeeper/sakis3g'
BINARY_LSUSB = '/usr/bin/lsusb'
BINARY_UMTSKEEPER = '/usr/umtskeeper/umtskeeper'
BINARY_KILLALL = '/usr/bin/killall'
BINARY_SYSTEMCTL = '/bin/systemctl'

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

dict_configuration = {'modem_list'      : None,
                      'modem_configured': None,
                      'dial'            : None,
                      'apn'             : None,
                      'username'        : None,
                      'password'        : None,
                      'sim_card_pin'    : None}

def test_connection():
    if execute_command(command_test_connection.split(' ')) != 0:
        exit(2)

    if execute_command([BINARY_KILLALL, '-9', 'pppd']) != 0:
        exit(1)
                
def create_execute_systemd_service():
    if execute_command([BINARY_SYSTEMCTL, 'enable', FILE_UNIT_TF_MOBILE_INTERNET]) != 0:
        disable_remove_systemd_service()
        exit(3)
    
    if execute_command([BINARY_SYSTEMCTL, 'start', SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) != 0:
        disable_remove_systemd_service()
        exit(4)
                
def stop_disable_remove_systemd_service():
    os.system(' stop '.join([BINARY_SYSTEMCTL, SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) + ' &> /dev/null')
    os.system(' disable '.join([BINARY_SYSTEMCTL, SERVICE_SYSTEMD_TF_MOBILE_INTERNET]) + ' &> /dev/null')
    
    if os.path.exists(FILE_UNIT_TF_MOBILE_INTERNET):
        os.remove(FILE_UNIT_TF_MOBILE_INTERNET)
                
def execute_command(command):
    p = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
    p.communicate()
    return p.returncode

def prepare_test_and_configuration(usb_modem,
                                   dial,
                                   apn,
                                   apn_user,
                                   apn_pass,
                                   sim_pin):
    command_test_connection = ''
    configuration_umtskeeper = ''
    sakis_operators = '''DIAL="{0}" APN="{1}" APN_USER="{2}" APN_PASS="{3}" OTHER="USBMODEM" USBMODEM="{4}"'''
    sakis_operators_sim_pin = '''SIM_PIN="{0}" DIAL="{1}" APN="{2}" APN_USER="{3}" APN_PASS="{4}" OTHER="USBMODEM" USBMODEM="{5}"'''

    if sim_pin:
        command_test_connection_args = ' connect --nostorage --pppd --nofix --console ' +\
            sakis_operators_sim_pin.format(sim_pin,
                                           dial,
                                           apn,
                                           apn_user,
                                           apn_pass,
                                           usb_modem)
        command_test_connection = BINARY_SAKIS3G + command_test_connection_args
        configuration_umtskeeper = CONFIG_UMTSKEEPER.format(sakis_operators_sim_pin.replace('"', "'").format(sim_pin,
                                                                                                             dial,
                                                                                                             apn,
                                                                                                             apn_user,
                                                                                                             apn_pass,
                                                                                                             usb_modem))
        return command_test_connection, configuration_umtskeeper

    else:
        command_test_connection_args = ' connect --nostorage --pppd --nofix --console ' +\
            sakis_operators.format(dial,
                                   apn,
                                   apn_user,
                                   apn_pass,
                                   usb_modem)
        command_test_connection = BINARY_SAKIS3G + command_test_connection_args
        configuration_umtskeeper = CONFIG_UMTSKEEPER.format(sakis_operators.replace('"', "'").format(dial,
                                                                                                     apn,
                                                                                                     apn_user,
                                                                                                     apn_pass,
                                                                                                     usb_modem))
        return command_test_connection, configuration_umtskeeper

def find_whole_word(word):
    return re.compile(r'\b({0})\b'.format(word), flags=re.IGNORECASE).search

def get_DNS():
    with open('/etc/resolv.conf', 'r') as rcfh:
        for line in rcfh.readlines():
            line_split = line.split(' ')

            if len(line_split) == 2 and \
               line_split[0] == 'nameserver' and line_split[1] != '':
                    return line_split[1].strip()

try:
    # Handle command GET_STATUS
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
            p = subprocess.Popen([BINARY_SYSTEMCTL,
                                  'status',
                                  SERVICE_SYSTEMD_TF_MOBILE_INTERNET],
                                 stdout = subprocess.PIPE,
                                 stderr = subprocess.PIPE)
            p_out_str = p.communicate()[0]
            
            if p_out_str and \
               'Loaded: loaded' in p_out_str and \
               'Active: active' in p_out_str:
                    dict_status['status'] = 'Connecting...'
            else:
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

    # Handle command REFRESH
    elif ACTION == 'REFRESH':
        p = subprocess.Popen([BINARY_LSUSB, '-v'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        p_out_str = p.communicate()[0]

        if p.returncode != 0:
            exit(1)

        if not p_out_str:
            exit(1)

        list_modem = []

        p_out_lines = p_out_str.splitlines()

        for i, line in enumerate(p_out_lines):
            if not line.startswith('Bus '):
                continue

            entry = line.split(': ')[1].split('ID ')[1].split(' ', 1)
            vid_pid = entry[0].strip()
            name = entry[1].strip()

            if not name:
                name = vid_pid

            dict_modem = {'vid_pid' : vid_pid,
                          'name': name}

            list_modem.append(dict_modem)

        # Load USB device list
        dict_configuration['modem_list'] = list_modem

        # Process configuration file if it exists
        if os.path.exists(FILE_CONFIG_UMTSKEEPER):
            with open(FILE_CONFIG_UMTSKEEPER, 'r') as ucfh:
                for line in ucfh.readlines():
                    if TAG_CONFIG_SAKIS_OPERATORS not in line:
                        continue

                    splitted_line = line.split('=', 1)
                    
                    if len(splitted_line) != 2:
                        continue

                    splitted_params = splitted_line[1].strip().split(' ')
                    
                    if len(splitted_params) < 1:
                        continue
                    
                    for raw_param in splitted_params:
                        splitted_raw_param = raw_param.split('=')
                        
                        if len(splitted_raw_param) != 2:
                            continue

                        if find_whole_word(TAG_PARAM_USBMODEM)(splitted_raw_param[0]):
                            dict_configuration['modem_configured'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                        elif find_whole_word(TAG_PARAM_DIAL)(splitted_raw_param[0]):
                            dict_configuration['dial'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')

                        elif find_whole_word(TAG_PARAM_APN)(splitted_raw_param[0]):
                            dict_configuration['apn'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')
                                
                        elif find_whole_word(TAG_PARAM_APN_USER)(splitted_raw_param[0]):
                            dict_configuration['username'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')
                                
                        elif find_whole_word(TAG_PARAM_APN_PASS)(splitted_raw_param[0]):
                            dict_configuration['password'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')
                        
                        elif find_whole_word(TAG_PARAM_SIM_PIN)(splitted_raw_param[0]):
                            dict_configuration['sim_card_pin'] =\
                                splitted_raw_param[1].strip().replace("'", '').replace('"', '')
                        
        sys.stdout.write(json.dumps(dict_configuration))

    # Handle command CONNECT
    elif ACTION == 'CONNECT':
        if len(sys.argv) < 8:
            exit(1)

        usb_modem = sys.argv[2]
        dial = sys.argv[3]
        apn = sys.argv[4]
        apn_user = sys.argv[5]
        apn_pass = sys.argv[6]
        sim_pin = sys.argv[7]

        command_test_connection, configuration_umtskeeper =\
            prepare_test_and_configuration(usb_modem,
                                           dial,
                                           apn,
                                           apn_user,
                                           apn_pass,
                                           sim_pin)

        # Test connection to verify provided configuration
        test_connection()

        # Write configuration file
        with open(FILE_CONFIG_UMTSKEEPER, 'w') as ucfh:
            ucfh.write(configuration_umtskeeper)

        # Diable and remove the systemd service if it exists
        stop_disable_remove_systemd_service()
        
        # Write the systemd unit file
        with open(FILE_UNIT_TF_MOBILE_INTERNET, 'w') as ufh:
            ufh.write(UNIT_SYSTEMD)

        create_execute_systemd_service()

    else:
        exit(1)

except:
    exit(1)
