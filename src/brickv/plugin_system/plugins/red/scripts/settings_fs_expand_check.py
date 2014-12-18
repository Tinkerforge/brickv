#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import subprocess
from sys import argv

if len(argv) < 2:
    exit(1)

block_device = unicode(argv[1])
return_dict = {}

cmd_get_part = '/bin/lsblk -o name -ln ' + block_device
ps_get_part = subprocess.Popen(cmd_get_part, shell=True, stdout=subprocess.PIPE)
cmd_output = ps_get_part.communicate()[0]

if ps_get_part.returncode:
    exit(1)
else:
    if len(cmd_output.splitlines()) != 2:
        exit(1)

try:
    with open('/sys/block/mmcblk0/size') as f_card_size:
        card_size = f_card_size.readline()
        return_dict['card_size'] = int(card_size.strip())

    with open('/sys/block/mmcblk0/mmcblk0p1/start') as f_p1_start:
        p1_start = f_p1_start.readline()
        return_dict['p1_start'] = int(p1_start.strip())

    with open('/sys/block/mmcblk0/mmcblk0p1/size') as f_p1_size:
        p1_size = f_p1_size.readline()
        return_dict['p1_size'] = int(p1_size.strip())
except:
    print(json.dumps(None))
    exit(1)

print(json.dumps(return_dict, separators=(',', ':')))
