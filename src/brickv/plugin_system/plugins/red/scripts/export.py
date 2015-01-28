#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import tarfile
import tempfile

programs = sys.argv[1:]

if len(programs) == 0:
    sys.stderr.write(u'Missing parameters'.encode('utf-8'))
    exit(1)

try:
    directory = tempfile.mkdtemp(prefix='tfrba-export-')
    archive = os.path.join(directory, 'archive.tfrba')
    version = os.path.join(directory, 'tfrba-version')

    os.chmod(directory, 0o755)

    with open(version, 'wb') as f:
        f.write('1')

    with tarfile.open(archive, 'w:gz') as f:
        f.add(version, 'tfrba-version')

        for program in programs:
            f.add(os.path.join('/', 'home', 'tf', 'programs', program),
                  os.path.join('programs', program))
except Exception as e:
    sys.stderr.write(unicode(e).encode('utf-8'))
    exit(2)

sys.stdout.write(unicode(directory).encode('utf-8'))
exit(0)
