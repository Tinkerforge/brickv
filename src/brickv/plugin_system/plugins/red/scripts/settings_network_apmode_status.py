#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces
import psutil

return_dict = {'ap_first_time'                 : None,
               'ap_incomplete_config'          : None,
               'ap_hardware_or_config_problem' : None}

try:
    return_dict['ap_first_time']  = False
    return_dict['ap_incomplete_config'] = True
    if os.path.isfile('/etc/hostapd/hostapd.conf') and \
       os.path.isfile('/etc/dnsmasq.conf'):
            with open('/etc/hostapd/hostapd.conf', 'r') as fd_hostapd_conf:
                lines = fd_hostapd_conf.readlines()

                for l in lines:
                    l_split = l.strip().split('=')
                    if len(l_split) == 2 and l_split[0].strip(' ') == 'interface':
                        if l_split[1]:
                            return_dict['ap_incomplete_config'] = False
                        else:
                            hostapd_running = False
                            for p in psutil.process_iter():
                                if p.name == 'hostapd':
                                    hostapd_running = True
                            if not hostapd_running:
                                return_dict['ap_first_time'] = True

    return_dict['ap_hardware_or_config_problem'] = True
    if not return_dict['ap_incomplete_config']:
        hostapd_running = False
        dnsmasq_running = False
        for p in psutil.process_iter():
            if p.name == 'hostapd':
                hostapd_running = True
            elif p.name == 'dnsmasq':
                dnsmasq_running = True

        if hostapd_running and dnsmasq_running:
            return_dict['ap_hardware_or_config_problem'] = False

except:
    exit(1)

print json.dumps(return_dict)
