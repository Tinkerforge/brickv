#!/usr/bin/env python2

import os
import json
import shutil
from sys import argv

if len(argv) < 3:
    print json.dumps(False)
    exit (0)

file_list = json.loads(argv[1])
dir_list = json.loads(argv[2])

if not isinstance(file_list, list) or\
   not isinstance(dir_list, list):
    print json.dumps(False)
    exit(0)

if len(file_list) <= 0 and\
   len(dir_list) <= 0:
    print json.dumps(False)
    exit(0)

if len(file_list) > 0:
    for f in file_list:
        file_path = unicode(f)
        if not os.path.exists(file_path):
            continue
        try:
            os.remove(file_path)
        except:
            print json.dumps(False)
            exit(0)

if len(dir_list) > 0:
    for d in dir_list:
        dir_path = unicode(d)
        if not os.path.isdir(dir_path):
            continue
        try:
            shutil.rmtree(dir_path)
        except:
            print json.dumps(False)
            exit(0)

print json.dumps(True)
