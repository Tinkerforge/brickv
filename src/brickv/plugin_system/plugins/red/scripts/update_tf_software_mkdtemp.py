#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import tempfile

t = tempfile.mkdtemp()
bindings = os.path.join(t, 'bindings')

if os.path.exists(bindings):
    shutil.rmtree(bindings)

os.makedirs(bindings)

sys.stdout.write(unicode(t).encode('utf-8'))
