#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import json
import os
import sys
import zlib


### SCRIPT-INCLUDE: ../java_utils.py


result = {}

if len(sys.argv) < 2 or not os.path.isdir(sys.argv[1]):
    sys.stderr.write(unicode('Missing or invalid script parameters (internal error)').encode('utf-8'))
    exit(1)

base = sys.argv[1]

try:
    for root, directories, files in os.walk(base):
        relative_root = os.path.relpath(root, base)

        for filename in files:
            if filename.endswith('.jar'):
                absolute = os.path.join(root, filename)

                try:
                    classes = get_jar_file_main_classes(absolute)
                except:
                    continue

                relative = os.path.join(relative_root, filename)

                for cls in classes:
                    result.setdefault(cls, []).append(relative)
            elif filename.endswith('.class'):
                try:
                    classes = get_class_file_main_classes(os.path.join(root, filename))
                except:
                    continue

                for cls in classes:
                    result.setdefault(cls, []).append(relative_root)
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
exit(0)
