#!/usr/bin/env python2

import json
import socket
import netifaces

return_dict = {}
return_dict['hostname'] = socket.gethostname()

return_dict['cconfig_ifs'] = {}

for i in netifaces.interfaces():
    addrs = netifaces.ifaddresses(i)
    if netifaces.AF_INET in addrs:
        addrs_inet = addrs[netifaces.AF_INET]
        addrs_inet[0]['addr']
        addrs_inet[0]['netmask']
        return_dict['cconfig_ifs'][i] = {'ip': addrs[netifaces.AF_INET][0]['addr'],
                                         'mask': addrs[netifaces.AF_INET][0]['netmask']}

gws = netifaces.gateways()
if 'default' in gws and netifaces.AF_INET in gws['default']:
    return_dict['cconfig_gateway']  = gws['default'][netifaces.AF_INET][0]
else:
    return_dict['cconfig_gateway'] = "None"

with open("/etc/resolv.conf", "r") as rcf:
    lines = rcf.readlines()
    for l in lines:
        if l.split(' ')[0] == "nameserver":
            return_dict['cconfig_dns'] = l.split(' ')[1]

print json.dumps(return_dict)
