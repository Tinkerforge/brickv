#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
from sys import argv

if len(argv) < 3:
    print json.dumps(False)
    exit(0)

rename_from = argv[1]
rename_to = argv[2]

try:
    if not os.path.exists(rename_from):
        print json.dumps(False)
        exit(0)
    if not os.path.isdir(rename_from):
        if not os.path.isfile(rename_from):
            print json.dumps(False)
            exit(0)
    os.rename(rename_from, rename_to)
    print json.dumps(True)
except:
    print json.dumps(False)
