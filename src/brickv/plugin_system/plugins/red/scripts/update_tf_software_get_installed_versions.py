#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import re
import sys
import json
import subprocess

BINDINGS_DIR = '/usr/tinkerforge/bindings/'
BINDINGS = ['c', 'csharp', 'delphi', 'java',
            'javascript', 'matlab', 'perl', 'php',
            'python', 'ruby', 'shell', 'vbnet']

return_dict = {'brickv': None, 'bindings':{}}

err = False
err_msg = ''

with open(os.devnull, 'w') as dev_null:
    dpkg = subprocess.Popen(['/usr/bin/dpkg','-s', 'brickv'],
                            stdout=subprocess.PIPE,
                            stderr=dev_null)

    grep = subprocess.Popen(['/bin/grep', 'Version:'],
                            stdin=dpkg.stdout,
                            stdout=subprocess.PIPE,
                            stderr=dev_null)

output_grep = None
(output_grep, _) = grep.communicate()

if output_grep is not None and type(output_grep) is str:
    output_grep_split = output_grep.split(':')

    if len(output_grep_split) != 2:
        err = True
        return_dict['brickv'] = '-'
        err_msg += 'Could not read Brick Viewer installed version\n'
    else:
        return_dict['brickv'] = output_grep_split[1].strip()
else:
    err = True
    err_msg += 'Could not read Brick Viewer installed version\n'

def get_changelog_version(bindings_root_directory):
    r1 = re.compile('^\d{4}-\d{2}-\d{2}:\s(\d+)\.(\d+)\.(\d+)\s\(')
    r2 = re.compile('^(\d+)\.(\d+)\.(\d+):')
    last = None

    with open(os.path.join(bindings_root_directory, 'changelog.txt'), 'rb') as f:
        for line in f.readlines():
            m = r1.match(line)

            if m == None:
                m = r2.match(line)

            if m is not None:
                last = (m.group(1), m.group(2), m.group(3))

    return last

for b in BINDINGS:
    try:
        path = os.path.join(BINDINGS_DIR, b)
        return_dict['bindings'][b] = '.'.join(get_changelog_version(path)).strip()
    except:
        err = True
        display_name = ''
        return_dict['bindings'][b] = '-'

        if b == 'c':
            display_name = 'C/C++ Bindings'
        elif b == 'csharp':
            display_name = 'C#/Mono Bindings'
        elif b == 'delphi':
            display_name = 'Delphi/Lazarus Bindings'
        elif b == 'java':
            display_name = 'Java Bindings'
        elif b == 'javascript':
            display_name = 'JavaScript Bindings'
        elif b == 'matlab':
            display_name = 'Octave Bindings'
        elif b == 'perl':
            display_name = 'Perl Bindings'
        elif b == 'php':
            display_name = 'PHP Bindings'
        elif b == 'python':
            display_name = 'Python Bindings'
        elif b == 'ruby':
            display_name = 'Ruby Bindings'
        elif b == 'shell':
            display_name = 'Shell Bindings'
        elif b == 'vbnet':
            display_name = 'VB.NET Bindings'

        err_msg += 'Could not read ' + display_name + ' installed version\n'

if err:
    sys.stderr.write(unicode(err_msg).encode('utf-8'))
    exit(1)

sys.stdout.write(json.dumps(return_dict, separators=(',', ':')))
