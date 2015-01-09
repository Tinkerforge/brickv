#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json

return_dict = {'ap_enabled': None}

try:
    with open('/etc/tf_image_version','r') as fd_tf_ver:
        line = fd_tf_ver.readline()
        if line:
            l_split = line.strip().split(' (')
            if len(l_split) > 1:
                img_ver = float(l_split[0])
                if img_ver > 1.3:
                    if os.path.isfile('/etc/tf_ap_enabled'):
                        return_dict['ap_enabled'] = True
                    else:
                        return_dict['ap_enabled'] = False
                else:
                    return_dict['ap_enabled'] = False
except:
    exit(1)

print json.dumps(return_dict)
