#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import sys

if len(sys.argv) < 2:
    sys.stderr.write(unicode('Missing script parameters (internal error)').encode('utf-8'))
    exit(1)

try:
    file_list = json.loads(sys.argv[1])
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

if not isinstance(file_list, list):
    sys.stderr.write(unicode('Invalid script parameters (internal error)').encode('utf-8'))
    exit(1)

for file_path in file_list:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            sys.stderr.write(unicode(e).encode('utf-8'))
            exit(2)

exit(0)
