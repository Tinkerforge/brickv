#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import json
import netifaces
import subprocess

return_dict = {'wireless': None,
               'wired': None,
               'wireless_links': None}

wl_links_dict = {}
lwireless = []
lwired = []

for intf in netifaces.interfaces():
     if os.path.isdir('/sys/class/net/'+intf+'/wireless'):
        lwireless.append(intf)
     else:
        lwired.append(intf)

if len(lwireless) > 0:
    return_dict['wireless'] = lwireless
    for wl_intf in lwireless:
        cmd_get_link = '/sbin/iwconfig '+wl_intf+' | /usr/bin/head -n2'
        ps_get_link = subprocess.Popen(cmd_get_link, shell=True, stdout=subprocess.PIPE)
        cmd_output = ps_get_link.communicate()[0]
        if ps_get_link.returncode:
            exit (1)

        wl_links_dict[wl_intf] =  {'name': wl_intf,
                                   'status': False,
                                   'essid': None,
                                   'bssid': None}

        cmd_output_lines = cmd_output.splitlines()
        if len(cmd_output_lines) >= 2 and cmd_output:
            if 'off/any' in cmd_output_lines[0] or 'unassociated' in cmd_output_lines[0]:
                continue
            cmd_output_line0_array = cmd_output_lines[0].split(' ')
            cmd_output_line1_array = cmd_output_lines[1].split('Access Point: ')
            if len(cmd_output_line0_array) >= 0:
                for token in cmd_output_line0_array:
                    if 'ESSID:' in token:
                        _associated_essid = token.split(':')[1]
                        associated_essid = _associated_essid[1:-1]
                        if len(cmd_output_line1_array) > 0:
                            associated_bssid = cmd_output_line1_array[-1:]
                            wl_links_dict[wl_intf] =  {'name': wl_intf,
                                                       'status': True,
                                                       'essid': associated_essid,
                                                       'bssid': associated_bssid}

#remove lo and tunl0 interfaces from interfaces list
lwired = [x for x in lwired if x!='lo' and x!='tunl0']

if len(lwired) > 0:
    return_dict['wired'] = lwired
if len(wl_links_dict) > 0:
 return_dict['wireless_links'] = wl_links_dict

print json.dumps(return_dict, separators=(',', ':'))
