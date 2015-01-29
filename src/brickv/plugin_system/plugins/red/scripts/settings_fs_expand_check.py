#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import subprocess
import sys

if len(sys.argv) < 2:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

block_device = sys.argv[1]
result = {}
cmd_get_part = '/bin/lsblk -o name -ln ' + block_device
ps_get_part = subprocess.Popen(cmd_get_part, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
cmd_output, cmd_error = ps_get_part.communicate()

if ps_get_part.returncode != 0:
    cmd_error = cmd_error.strip()

    if len(cmd_error) > 0:
        sys.stderr.write(u'Could not get block devices list:\n\n{0}'.format(cmd_error).encode('utf-8'))
    else:
        sys.stderr.write(u'Could not get block devices list'.encode('utf-8'))

    exit(ps_get_part.returncode)
elif len(cmd_output.splitlines()) != 2:
    exit(3)

try:
    with open('/sys/block/mmcblk0/size') as f_card_size:
        card_size = f_card_size.readline()
        result['card_size'] = int(card_size.strip())

    with open('/sys/block/mmcblk0/mmcblk0p1/start') as f_p1_start:
        p1_start = f_p1_start.readline()
        result['p1_start'] = int(p1_start.strip())

    with open('/sys/block/mmcblk0/mmcblk0p1/size') as f_p1_size:
        p1_size = f_p1_size.readline()
        result['p1_size'] = int(p1_size.strip())
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(4)

sys.stdout.write(json.dumps(result, separators=(',', ':')))
exit(0)
