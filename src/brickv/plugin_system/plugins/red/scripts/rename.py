#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os

if len(sys.argv) < 3:
    sys.stderr.write(unicode('Missing script parameters (internal error)').encode('utf-8'))
    exit(1)

try:
    os.rename(sys.argv[1], sys.argv[2])
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

exit(0)
