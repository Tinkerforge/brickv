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
     if os.path.isdir("/sys/class/net/"+intf+"/wireless"):
        lwireless.append(intf)
     else:
        lwired.append(intf)

if len(lwireless) > 0:
    return_dict['wireless'] = lwireless
    for wl_intf in lwireless:
            cmd_get_link = "/sbin/iw dev "+ wl_intf +" link | /usr/bin/head -n2"
            ps_get_link = subprocess.Popen(cmd_get_link, shell=True, stdout=subprocess.PIPE)
            cmd_output = ps_get_link.communicate()[0]
            if ps_get_link.returncode:
                exit (1)
            if cmd_output == "Not connected.\n" or cmd_output == "":
                wl_links_dict[wl_intf] =  {'name': wl_intf,
                                           'status': False,
                                           'essid': None,
                                           'bssid': None}
            else:
                cmd_output_first_split = cmd_output.split('\n')
                wl_links_dict[wl_intf] =  {'name': wl_intf,
                                           'status': True,
                                           'essid': cmd_output_first_split[1].strip().split('SSID: ')[1],
                                           'bssid': cmd_output_first_split[0].strip().split('Connected to ')[1].split(' (')[0]}

#remove lo and tunl0 interfaces from interfaces list
lwired = [x for x in lwired if x!='lo' and x!='tunl0']

if len(lwired) > 0:
    return_dict['wired'] = lwired
if len(wl_links_dict) > 0:
 return_dict['wireless_links'] = wl_links_dict

print json.dumps(return_dict, separators=(',', ':'))
