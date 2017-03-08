#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re
import json
import subprocess

BINDINGS_DIR = '/usr/tinkerforge/bindings/'
BINDINGS = ['c', 'csharp', 'delphi', 'java', 'javascript', 'matlab', 'perl', 'php', 'python', 'ruby', 'shell', 'vbnet']

return_dict = {'brickv': None, 'bindings':{}}

# Get Brickv version.
dpkg = subprocess.Popen(['/usr/bin/dpkg','-s', 'brickv'], stdout=subprocess.PIPE)
grep = subprocess.Popen(['/bin/grep', 'Version:'], stdin=dpkg.stdout, stdout=subprocess.PIPE)
(output_grep, ret_grep) = grep.communicate()
output_grep_split = output_grep.split(':')

if len(output_grep_split) != 2:
    return_dict['brickv'] = '-'
else:
    return_dict['brickv'] = output_grep_split[1].strip()

def get_changelog_version(bindings_root_directory):
    r = re.compile('^(\d{4}-\d{2}-\d{2}:\s)(\d+)\.(\d+)\.(\d+)\s\(')
    last = None

    with open(os.path.join(bindings_root_directory, 'changelog.txt'), 'rb') as f:
        for line in f.readlines():
            m = r.match(line)

            if m is not None:
                last = (m.group(2), m.group(3), m.group(4))

    return last

# Get version of each binding.
for b in BINDINGS:
    try:
        path = os.path.join(BINDINGS_DIR, b)
        return_dict['bindings'][b] = '.'.join(get_changelog_version(path)).strip()
    except:
        return_dict['bindings'][b] = '-'

print json.dumps(return_dict, separators=(',', ':'))
