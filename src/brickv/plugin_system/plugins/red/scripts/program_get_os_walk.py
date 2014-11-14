#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
from sys import argv, stdout
import zlib

return_os_walk_list = []

def output(data):
    stdout.write(zlib.compress(json.dumps(data, separators=(',', ':'))))

if len(argv) < 2:
    output(None)
    exit(0)
if not os.path.isdir(argv[1]):
    output(None)
    exit(0)

try:
    for root, dirs, files in os.walk(argv[1], topdown=True):
        files_with_size = []
        if len(files) > 0:
            for f in files:
                f_path = os.path.join(root, f)
                files_with_size.append({'name':f, 'size':os.stat(f_path).st_size})

        return_os_walk_list.append({'root': root,
                                    'dirs': dirs,
                                    'files': files_with_size})
except:
    output(None)
    exit(0)

output(return_os_walk_list)
