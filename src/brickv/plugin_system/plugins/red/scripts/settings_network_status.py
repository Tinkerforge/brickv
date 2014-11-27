#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import socket
import netifaces
import subprocess

return_dict = {}
return_dict['cstat_hostname'] = None
return_dict['cstat_intf_active'] = {'name': None, 'ip': None, 'mask': None}
return_dict['cstat_gateway'] = None
return_dict['cstat_dns'] = None

try:
    hname = unicode(socket.gethostname())
    if hname != "":
        return_dict['cstat_hostname'] = hname
except:
    pass

try:
    cmd_get_if_ok = "ip route | head -1 | awk -F' ' '{print $1}'"
    ps_get_if_ok = subprocess.Popen(cmd_get_if_ok, shell=True, stdout=subprocess.PIPE)
    intf_ok = ps_get_if_ok.communicate()[0].strip()
    if intf_ok == "default":
        cmd_get_if_active = "ip route | head -1 | awk -F' ' '{print $5}'"
        ps_get_if_active = subprocess.Popen(cmd_get_if_active, shell=True, stdout=subprocess.PIPE)
        intf_active = ps_get_if_active.communicate()[0].strip()
    else:
        intf_active == ""

    if intf_active != "":
        return_dict['cstat_intf_active']['name'] = intf_active
        intf_addrs = netifaces.ifaddresses(intf_active)
        if netifaces.AF_INET in intf_addrs and\
           'addr' in intf_addrs[netifaces.AF_INET][0] and\
           'netmask' in intf_addrs[netifaces.AF_INET][0]:
            return_dict['cstat_intf_active']['ip'] = intf_addrs[netifaces.AF_INET][0]['addr']
            return_dict['cstat_intf_active']['mask'] = intf_addrs[netifaces.AF_INET][0]['netmask']

    gws = netifaces.gateways()
    if 'default' in gws and netifaces.AF_INET in gws['default']:
        return_dict['cstat_gateway']  = gws['default'][netifaces.AF_INET][0]
except:
    pass

try:
    with open("/etc/resolv.conf", "r") as rcf:
        lines = rcf.readlines()
        for i, l in enumerate(lines):
            l_splitted = l.split(' ')
            if l_splitted[0] == "nameserver" and l_splitted[1] != "":
                return_dict['cstat_dns'] = l_splitted[1]
                break
except:
    pass

print json.dumps(return_dict)
