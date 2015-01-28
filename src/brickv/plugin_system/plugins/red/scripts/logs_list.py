#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import stat
import sys
import zlib

result = {}

if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
    sys.stderr.write(u'Missing or invalid parameters'.encode('utf-8'))
    exit(2)

base = sys.argv[1]

try:
    for name in os.listdir(base):
        if not name.endswith('_stdout.log') and not name.endswith('_stderr.log'):
            continue

        st = os.lstat(os.path.join(base, name))

        if stat.S_ISREG(st.st_mode):
            result[name] = st.st_size
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
exit(0)
