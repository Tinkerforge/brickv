#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json

return_dict = {}

try:
    with open('/sys/block/mmcblk0/size') as f_card_size:
        card_size = f_card_size.readline()
        return_dict['card_size'] = int(card_size.strip())
    
    with open('/sys/block/mmcblk0/mmcblk0p1/size') as f_p1_size:
        p1_size = f_p1_size.readline()
        return_dict['p1_size'] = int(p1_size.strip())
except:
    json.dumps(None)
    exit(1)

json.dumps(return_dict)
