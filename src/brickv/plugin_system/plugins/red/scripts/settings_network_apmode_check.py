#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces
import psutil

return_dict = {'ap_interface': None,
               'ap_active':    None}

try:
    for intf in netifaces.interfaces():
        if os.path.isdir('/sys/class/net/'+intf+'/wireless'):
            return_dict['ap_interface'] = True
            break
        else:
            return_dict['ap_interface'] = False

    if not return_dict['ap_interface']:
        return_dict['ap_active'] = False
    else:
        if os.path.isfile('/etc/hostapd/hostapd.conf'):
            interface_available = False
            hostapd_running = False
            dnsmasq_running = False

            with open('/etc/hostapd/hostapd.conf', 'r') as fd_hostapd_conf:
                lines = fd_hostapd_conf.readlines()

            for l in lines:
                if 'interface' not in l:
                    continue
                l_split = l.strip().split('=')

                if len(l_split) != 2:
                    continue

                interface = l_split[1].strip(' ')
                break

            if not interface:
                return_dict['ap_active'] = False
            else:
                for intf in netifaces.interfaces():
                    if intf == interface:
                        interface_available = True
                        break

            if interface_available:
                for p in psutil.process_iter():
                    if p.name == 'hostapd':
                        hostapd_running = True
                    elif p.name == 'dnsmasq':
                        dnsmasq_running = True

                if hostapd_running and dnsmasq_running:
                    return_dict['ap_active'] = True
                else:
                    return_dict['ap_active'] = False
            else:
                return_dict['ap_active'] = False
        else:
            return_dict['ap_active'] = False

except:
    exit(1)

print json.dumps(return_dict)
