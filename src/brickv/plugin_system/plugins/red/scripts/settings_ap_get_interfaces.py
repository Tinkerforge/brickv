#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces

return_dict = {}

try:
    for intf in netifaces.interfaces():
        if not os.path.isdir('/sys/class/net/'+intf+'/wireless'):
            continue

        intf_dict = {'ip'  : None,
                     'mask': None}

        return_dict[intf] = intf_dict

        intf_addrs = netifaces.ifaddresses(intf)

        if netifaces.AF_INET in intf_addrs and\
           'addr' in intf_addrs[netifaces.AF_INET][0] and\
           'netmask' in intf_addrs[netifaces.AF_INET][0]:
                return_dict[intf]['ip'] = intf_addrs[netifaces.AF_INET][0]['addr']
                return_dict[intf]['mask'] = intf_addrs[netifaces.AF_INET][0]['netmask']
                
except:
    exit(1)

print json.dumps(return_dict)
