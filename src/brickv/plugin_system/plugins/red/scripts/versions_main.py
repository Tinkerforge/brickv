#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re

BINDINGS_DIR = '/usr/tinkerforge/bindings/'
BINDINGS = ['c', 'csharp', 'delphi', 'java', 'javascript', 'matlab', 'perl', 'php', 'python', 'ruby', 'shell', 'vbnet']

def get_changelog_version(bindings_root_directory):
    r1 = re.compile('^\d{4}-\d{2}-\d{2}:\s(\d+)\.(\d+)\.(\d+)\s\(')
    r2 = re.compile('^(\d+)\.(\d+)\.(\d+):')
    last = None

    with open(os.path.join(bindings_root_directory, 'changelog.txt'), 'rb') as f:
        for line in f.readlines():
            m = r1.match(line)

            if m == None:
                m = r2.match(line)

            if m != None:
                last = (m.group(1), m.group(2), m.group(3))

    return last

os.system('/usr/bin/brickd --version')
os.system('/usr/bin/redapid --version')
os.system('/bin/cat /etc/tf_image_version')

for b in BINDINGS:
    try:
        path = os.path.join(BINDINGS_DIR, b)
        print('.'.join(get_changelog_version(path)))
    except:
        print('Unknown')
