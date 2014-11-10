#!/usr/bin/env python2

import os
import json
from sys import argv

if len(argv) < 2:
    print json.dumps(False)
    exit (0)

rename_list = json.loads(argv[1])

if not isinstance(rename_list, list):
    print json.dumps(False)
    exit(0)

if len(rename_list) != 2:
    print json.dumps(False)
    exit(0)

rename_from = unicode(rename_list[0])
rename_to = unicode(rename_list[1])

try:
    if not os.path.exists(rename_from):
        print json.dumps(False)
        exit(0)
    if not os.path.isdir(rename_from):
        if not os.path.isfile(rename_from):
            print json.dumps(False)
            exit(0)
    os.rename(rename_from, rename_to)
except:
    print json.dumps(False)
    exit(0)

print json.dumps(True)
