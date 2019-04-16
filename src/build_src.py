#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>
Copyright (C) 2019 Matthias Bolte <matthias@tinkerforge.com>

build_src.py: Generate UI files and other code

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import sys
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

basedir = os.path.dirname(os.path.realpath(__file__))
brickv = os.path.join(basedir, 'brickv')

for dirpath, dirnames, filenames in os.walk(brickv):
    if 'build_extra.py' in filenames:
        print('calling build_extra.py in ' + os.path.relpath(dirpath, basedir))
        os.chdir(dirpath)
        system(sys.executable + ' build_extra.py')

    if os.path.basename(dirpath) != 'ui':
        continue

    for filename in filenames:
        name, ext = os.path.splitext(filename)

        if ext != '.ui':
            continue

        out_file = os.path.normpath(os.path.join(dirpath, "..", "ui_" + name + ".py"))
        in_file = os.path.join(dirpath, filename)

        # Arch Linux complains, if a built package contains references to $SRCDIR.
        # (e.g. the directory in which the package was built)
        # Thus use the relative path here, as pyuic writes the in_file path it is called with into the out file.
        in_file = os.path.relpath(in_file, basedir)
        print('building ' + in_file)
        os.chdir(basedir)
        system(sys.executable + " pyuic5-fixed.py -o " + out_file + " " + in_file)

args = ' '.join(sys.argv[1:])
print('calling build_plugin_list.py ' + args)
os.chdir(basedir)
system(sys.executable + ' build_plugin_list.py ' + args)
