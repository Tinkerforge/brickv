#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
import shutil
import sys

if len(sys.argv) < 3:
    sys.stderr.write(unicode('Missing script parameters (internal error)').encode('utf-8'))
    exit(1)

try:
    file_list = json.loads(sys.argv[1])
    dir_list  = json.loads(sys.argv[2])
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

if not isinstance(file_list, list) or not isinstance(dir_list, list):
    sys.stderr.write(unicode('Invalid script parameters (internal error)').encode('utf-8'))
    exit(1)

for file_path in file_list:
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            sys.stderr.write(unicode(e).encode('utf-8'))
            exit(2)

for dir_path in dir_list:
    if os.path.isdir(dir_path):
        try:
            shutil.rmtree(dir_path)
        except Exception as e:
            sys.stderr.write(unicode(e).encode('utf-8'))
            exit(2)

exit(0)
