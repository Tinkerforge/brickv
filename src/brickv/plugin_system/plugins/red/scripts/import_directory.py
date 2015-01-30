#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import tempfile

try:
    directory = tempfile.mkdtemp(prefix='tfrba-import-')
    os.chmod(directory, 0o755)
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

sys.stdout.write(unicode(directory).encode('utf-8'))
exit(0)
