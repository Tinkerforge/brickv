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
        files_with_size = []
        if len(files) > 0:
            for f in files:
                f_path = os.path.join(root, f)
                files_with_size.append({'name':f, 'size':os.stat(f_path).st_size})

        return_os_walk_list.append({'root': root,
                                    'dirs': dirs,
                                    'files': files_with_size})
except:
    print json.dumps(None)
    exit (0)

print json.dumps(return_os_walk_list)
