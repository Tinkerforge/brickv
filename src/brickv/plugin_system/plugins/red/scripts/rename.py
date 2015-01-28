#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import os

if len(sys.argv) < 3:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(2)

try:
    os.rename(sys.argv[1], sys.argv[2])
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

exit(0)
