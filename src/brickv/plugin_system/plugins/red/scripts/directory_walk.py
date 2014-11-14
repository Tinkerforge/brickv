#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
from sys import argv, stdout
import zlib

result = {}

def output(data):
    stdout.write(zlib.compress(json.dumps(data, separators=(',', ':'))))

if len(argv) < 2 or not os.path.isdir(argv[1]):
    output(None)
    exit(0)

base = argv[1]

try:
    for root, directories, files in os.walk(base):
        relative_root = os.path.relpath(root, base)
        children      = result.setdefault('c', {})

        if relative_root != '.':
            for part in relative_root.split('/'):
                directory = children.setdefault(part, {})
                children  = directory.setdefault('c', {})

                if 'l' not in directory:
                    directory['l'] = int(os.lstat(root).st_mtime)

        for filename in files:
            absolute           = os.path.join(root, filename)
            st                 = os.lstat(absolute)
            children[filename] = {'s': st.st_size, 'l': int(st.st_mtime)}
except:
    output(None)
    exit(0)

output(result)
