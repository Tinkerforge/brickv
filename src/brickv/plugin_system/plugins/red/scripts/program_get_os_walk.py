#!/usr/bin/env python2

import os
import json
from sys import argv

return_os_walk_list = []

if len(argv) < 2:
    print json.dumps(None)
    exit (0)
if not os.path.isdir(str(argv[1])):
    print json.dumps(None)
    exit (0)

try:
    for root, dirs, files in os.walk(str(argv[1]), topdown=True):
        return_os_walk_list.append({'root': root,
                                    'dirs': dirs,
                                    'files': files})
except:
    print json.dumps(None)
    exit (0)

print json.dumps(return_os_walk_list)
