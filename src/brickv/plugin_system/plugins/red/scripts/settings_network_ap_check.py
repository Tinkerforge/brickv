#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import netifaces

return_dict = {'ap_image_version': None,
               'ap_interface'    : None,
               'ap_enabled'      : None}

try:
    with open('/etc/tf_image_version','r') as fd_tf_ver:
        line = fd_tf_ver.readline()
        if line:
            l_split = line.strip().split(' (')
            if len(l_split) > 1:
                img_ver = float(l_split[0])
                if img_ver > 1.3:
                    return_dict['ap_image_version'] = True
                else:
                    return_dict['ap_image_version'] = False

    for intf in netifaces.interfaces():
        if os.path.isdir('/sys/class/net/'+intf+'/wireless'):
            return_dict['ap_interface'] = True
            break
        else:
            return_dict['ap_interface'] = False

    if os.path.isfile('/etc/tf_ap_enabled'):
        return_dict['ap_enabled'] = True
    else:
        return_dict['ap_enabled'] = False
except:
    exit(1)

print json.dumps(return_dict)
