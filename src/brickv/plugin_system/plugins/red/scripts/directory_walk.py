#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import json
from sys import argv

result = {}

if len(argv) < 2 or not os.path.isdir(unicode(argv[1])):
    print json.dumps(None)
    exit(0)

base = unicode(argv[1])

try:
    for root, directories, files in os.walk(base):
        relative_root = os.path.relpath(root, base)
        children = result.setdefault('c', {})

        if relative_root != '.':
            for part in relative_root.split('/'):
                children = children.setdefault(part, {}).setdefault('c', {})

        for filename in files:
            absolute = os.path.join(root, filename)
            st = os.lstat(absolute)
            children[filename] = {'m': st.st_mode, 's': st.st_size, 'l': int(st.st_mtime)}
except:
    print json.dumps(None)
    exit(0)

print json.dumps(result, separators=(',', ':'))
