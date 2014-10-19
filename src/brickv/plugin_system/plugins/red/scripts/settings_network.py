#!/usr/bin/env python2

import json
import socket
import netifaces
import ConfigParser
import subprocess

return_dict = {}
return_dict['cstat_hostname'] = None
return_dict['cstat_ifs'] = {}
return_dict['cstat_ifs']['active'] = {}
return_dict['cstat_ifs']['wireless'] = {}
return_dict['cstat_ifs']['wired'] = {}

try:
    hname = socket.gethostname()
    if hname != "":
        return_dict['cstat_hostname'] = hname
except:
    return_dict['cstat_hostname'] = None

return_dict['cstat_ifs']['active']['if_name'] = None
return_dict['cstat_ifs']['active']['ip'] = "None"
return_dict['cstat_ifs']['active']['mask'] = "None"

return_dict['cstat_ifs']['wireless']['if_name'] = None
return_dict['cstat_ifs']['wireless']['ip'] = "None"
return_dict['cstat_ifs']['wireless']['mask'] = "None"

return_dict['cstat_ifs']['wired']['if_name'] = None
return_dict['cstat_ifs']['wired']['ip'] = "None"
return_dict['cstat_ifs']['wired']['mask'] = "None"

try:
    cmd_get_if_active = "ip route | head -1 | awk -F' ' '{print $5}'"
    ps_get_if_active = subprocess.Popen(cmd_get_if_active, shell=True, stdout=subprocess.PIPE)
    if_active = ps_get_if_active.communicate()[0].strip()
    if if_active != "":
        return_dict['cstat_ifs']['active']['if_name'] = if_active
except:
    return_dict['cstat_ifs']['active']['if_name'] = None

with open("/etc/wicd/manager-settings.conf") as fh_wicd_manager_settings:
    cfg_parser = ConfigParser.ConfigParser()
    cfg_parser.readfp(fh_wicd_manager_settings)
    try:
        return_dict['cstat_ifs']['wireless']['if_name'] =  cfg_parser.get("Settings", "wireless_interface")
    except:
        return_dict['cstat_ifs']['wireless']['if_name'] = None
    try:
        return_dict['cstat_ifs']['wired']['if_name'] = cfg_parser.get("Settings", "wired_interface")
    except:
        return_dict['cstat_ifs']['wired']['if_name'] = None

if return_dict['cstat_ifs']['active']['if_name'] is not None:
    addrs = netifaces.ifaddresses(return_dict['cstat_ifs']['active']['if_name'])
    if netifaces.AF_INET in addrs and 'addr' in addrs[netifaces.AF_INET][0]:
        return_dict['cstat_ifs']['active']['ip'] = addrs[netifaces.AF_INET][0]['addr']
        return_dict['cstat_ifs']['active']['mask'] = addrs[netifaces.AF_INET][0]['netmask']
else:
    return_dict['cstat_ifs']['active']['if_name'] = "None"

if return_dict['cstat_ifs']['wireless']['if_name'] is not None and\
   return_dict['cstat_ifs']['wireless']['if_name'] in netifaces.interfaces():
    addrs = netifaces.ifaddresses(return_dict['cstat_ifs']['wireless']['if_name'])
    if netifaces.AF_INET in addrs and 'addr' in addrs[netifaces.AF_INET][0]:
        return_dict['cstat_ifs']['wireless']['ip'] = addrs[netifaces.AF_INET][0]['addr']
        return_dict['cstat_ifs']['wireless']['mask'] = addrs[netifaces.AF_INET][0]['netmask']
else:
    return_dict['cstat_ifs']['wireless']['if_name'] = "None"

if return_dict['cstat_ifs']['wired']['if_name'] is not None and\
   return_dict['cstat_ifs']['wired']['if_name'] in netifaces.interfaces():
    addrs = netifaces.ifaddresses(return_dict['cstat_ifs']['wired']['if_name'])
    if netifaces.AF_INET in addrs  and 'addr' in addrs[netifaces.AF_INET][0]:
        return_dict['cstat_ifs']['wired']['ip'] = addrs[netifaces.AF_INET][0]['addr']
        return_dict['cstat_ifs']['wired']['mask'] = addrs[netifaces.AF_INET][0]['netmask']
else:
    return_dict['cstat_ifs']['wired']['if_name'] = "None"

try:
    gws = netifaces.gateways()
    if 'default' in gws and netifaces.AF_INET in gws['default']:
        return_dict['cstat_gateway']  = gws['default'][netifaces.AF_INET][0]
    else:
        return_dict['cstat_gateway'] = "None"
except:
    return_dict['cstat_gateway'] = "None"

try:
    with open("/etc/resolv.conf", "r") as rcf:
        lines = rcf.readlines()
        for i, l in enumerate(lines):
            l_splitted = l.split(' ')
            if l_splitted[0] == "nameserver" and l_splitted[1] != "":
                return_dict['cstat_dns'] = l_splitted[1]
                break
            elif i == len(lines) - 1:
                return_dict['cstat_dns'] = "None"
except:
    return_dict['cstat_dns'] = "None"

print json.dumps(return_dict)
