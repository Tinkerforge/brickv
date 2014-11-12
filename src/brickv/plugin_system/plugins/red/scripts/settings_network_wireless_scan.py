#!/usr/bin/env python2

import json
import subprocess

return_dict = None
wlscan_cmd = "/usr/bin/wicd-cli --wireless -Sl"

wlscan_ps = subprocess.Popen(wlscan_cmd, shell=True, stdout=subprocess.PIPE)
wlscan_output = wlscan_ps.communicate()[0]

if wlscan_output != "":
    return_dict = {}
    _lines = wlscan_output.split('\n')
    for l in _lines:
        lsplitted = l.split('\t')
        if len(lsplitted) == 1:
            continue
        _apdict = {'essid': lsplitted[0],
                   'bssid': lsplitted[1],
                   'channel': lsplitted[2]}
        return_dict[lsplitted[3]] = _apdict

    for key, value in return_dict.iteritems():
        netdetail_cmd = "/usr/bin/wicd-cli --wireless -n"+key+" -d"
        netdetail_ps = subprocess.Popen(netdetail_cmd, shell=True, stdout=subprocess.PIPE)
        netdetail_output = netdetail_ps.communicate()[0]
        lines = netdetail_output.split('\n')
        for l in lines:
            lsplitted = l.split(': ')
            if lsplitted[0] == "Encryption":
                return_dict[key]['encryption'] = lsplitted[1]
            elif lsplitted[0] == "Encryption Method":
                return_dict[key]['encryption_method'] = lsplitted[1]

print json.dumps(return_dict, separators=(',', ':'))
