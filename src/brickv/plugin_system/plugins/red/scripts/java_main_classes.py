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
        for filename in files:
            if filename.endswith('.jar'):
                absolute = os.path.join(root, filename)

                try:
                    classes = get_jar_file_main_classes(absolute)
                except:
                    continue

                if len(classes) > 0:
                    result[absolute] = classes
            elif filename.endswith('.class'):
                try:
                    classes = get_class_file_main_classes(os.path.join(root, filename))
                except:
                    continue
                
                if len(classes) > 0:
                    if root in result:
                        result[root].extend(classes)
                    else:
                        result[root] = classes
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(3)

sys.stdout.write(zlib.compress(json.dumps(result, separators=(',', ':'))))
exit(0)
