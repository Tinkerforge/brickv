#!/usr/bin/env python2

import sys
import json
import netifaces
import subprocess

return_dict = {'status': 'disconnected',
               'essid': None,
               'bssid': None}

if len(sys.argv) < 2:
    print json.dumps(return_dict)
    exit (0)

if sys.argv[1] in netifaces.interfaces():
        cmd_get_link = "/sbin/iw dev "+ sys.argv[1] +" link | /usr/bin/head -n2"
        ps_get_link = subprocess.Popen(cmd_get_link, shell=True, stdout=subprocess.PIPE)
        cmd_output = ps_get_link.communicate()[0]
        if cmd_output == "Not connected.\n" or cmd_output == "":
            pass
        else:
            cmd_output_first_split = cmd_output.split('\n')
            return_dict['status'] = 'connected'
            return_dict['essid'] = cmd_output_first_split[1].strip().split('SSID: ')[1]
            return_dict['bssid'] = cmd_output_first_split[0].strip().split('Connected to ')[1].split(' (')[0]

print json.dumps(return_dict)
