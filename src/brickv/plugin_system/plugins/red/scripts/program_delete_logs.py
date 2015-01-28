#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import sys

if len(sys.argv) < 2:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

try:
    file_list = json.loads(sys.argv[1])
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

if not isinstance(file_list, list):
    sys.stderr.write(u'Invalid parameters'.encode('utf-8'))
    exit(4)

for file_path in file_list:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            sys.stderr.write(unicode(e).encode('utf-8'))
            exit(5)

exit(0)
