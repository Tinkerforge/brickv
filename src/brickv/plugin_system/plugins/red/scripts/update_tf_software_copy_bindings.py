#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import shutil

BINDINGS = ['c', 'csharp', 'delphi', 'java', 'javascript', 'matlab',
            'perl', 'php', 'python', 'ruby', 'shell', 'vbnet']

if len(sys.argv) != 2:
    sys.stderr.write(u'Wrong number of parameters provided'.encode('utf-8'))
    exit(1)

for di in os.listdir(sys.argv[1]):
    if not os.path.isdir(os.path.join(sys.argv[1], di)):
        continue

    for b in BINDINGS:
        if di != b:
            continue

        bindings_path = os.path.join('/usr/tinkerforge/bindings', b)

        if not os.path.isdir(bindings_path):
            continue

        shutil.rmtree(bindings_path)
        shutil.copytree(os.path.join(sys.argv[1], b), bindings_path)
