#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import sys
import zlib

result = {}

if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
    sys.stderr.write(unicode('Missing or invalid script parameters (internal error)').encode('utf-8'))
    exit(1)

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
                    directory['l'] = int(os.lstat(root).st_mtime)

        for filename in files:
            absolute           = os.path.join(root, filename)
            st                 = os.lstat(absolute)
            children[filename] = {'s': st.st_size, 'l': int(st.st_mtime)}
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
exit(0)
