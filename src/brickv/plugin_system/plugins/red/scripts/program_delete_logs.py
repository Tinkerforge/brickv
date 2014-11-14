#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
from sys import argv

if len(argv) < 2:
    print json.dumps(False)
    exit (0)

file_list = json.loads(argv[1])

if not isinstance(file_list, list):
    print json.dumps(False)
    exit(0)

if len(file_list) <= 0:
    print json.dumps(False)
    exit(0)

for f in file_list:
    try:
        os.remove(f)
    except:
        print json.dumps(False)
        exit(0)

print json.dumps(True)
