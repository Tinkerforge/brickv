#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import sys
import zlib

result = {}

if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
    sys.stderr.write(u'Missing or invalid parameters'.encode('utf-8'))
    exit(2)

base = sys.argv[1]

try:
    for root, directories, files in os.walk(base):
        relative_root = os.path.relpath(root, base)
        children      = result.setdefault('c', {})

        if relative_root != '.':
            for part in relative_root.split('/'):
                directory = children.setdefault(part, {})
                children  = directory.setdefault('c', {})

                if 'l' not in directory:
                    st             = os.lstat(root)
                    directory['l'] = int(st.st_mtime)
                    directory['p'] = int(st.st_mode)

        for filename in files:
            absolute           = os.path.join(root, filename)
            st                 = os.lstat(absolute)
            children[filename] = {'s': st.st_size, 'l': int(st.st_mtime), 'p': int(st.st_mode)}
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
exit(0)
