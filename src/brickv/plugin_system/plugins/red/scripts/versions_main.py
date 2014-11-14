#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re

BINDINGS_DIR = "/usr/tinkerforge/bindings/"
BINDINGS = ["csharp", "c", "delphi", "java", "javascript", "matlab", "perl", "php", "python", "ruby", "shell", "vbnet"]

def get_changelog_version(bindings_root_directory):
    r = re.compile('^(\d+)\.(\d+)\.(\d+):')
    last = None

    for line in file(os.path.join(bindings_root_directory, 'changelog.txt'), 'rb').readlines():
        m = r.match(line)

        if m is not None:
            last = (m.group(1), m.group(2), m.group(3))

    return last

os.system('/usr/bin/brickd --version')
os.system('/usr/bin/redapid --version')
os.system('/bin/cat /etc/tf_image_version')


for b in BINDINGS:
    try:
        path = os.path.join(BINDINGS_DIR, b)
        print '.'.join(get_changelog_version(path))
    except:
        print 'Unknown'
