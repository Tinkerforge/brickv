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

# build .ui files and call build_extra.py scripts
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

# build plugins list
imports_all = []
imports_released = []
device_classes_all = []
device_classes_released = []
plugins = os.path.join(basedir, 'brickv', 'plugin_system', 'plugins')
bindings = os.path.join(basedir, 'brickv', 'bindings')

for plugin in sorted(os.listdir(plugins)):
    if '__pycache__' in plugin:
        continue

    if not os.path.isfile(os.path.join(plugins, plugin, '__init__.py')):
        continue

    brick_binding = os.path.join(bindings, 'brick_{0}.py'.format(plugin))
    bricklet_binding = os.path.join(bindings, 'bricklet_{0}.py'.format(plugin))
    released = True

    if os.path.isfile(brick_binding):
        with open(brick_binding, 'r') as f:
            released = not '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read()
    elif os.path.isfile(bricklet_binding):
        with open(bricklet_binding, 'r') as f:
            released = not '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read()
    else:
        raise Exception('No bindings found corresponding to plugin ' + plugin)

    import_ = 'from brickv.plugin_system.plugins.{0} import device_class as {0}\n'.format(plugin)
    device_class = '    {0},\n'.format(plugin)

    imports_all.append(import_)
    device_classes_all.append(device_class)

    if released:
        imports_released.append(import_)
        device_classes_released.append(device_class)

for path, imports, device_classes in [(os.path.join(plugins, '__init__.py'), imports_all, device_classes_all),
                                      (os.path.join(basedir, 'released_plugins.py'), imports_released, device_classes_released)]:
    print('building ' + os.path.relpath(path, basedir))

    with open(path, 'w') as f:
        f.writelines(imports)
        f.write('\n')
        f.write('device_classes = [\n')
        f.writelines(device_classes)
        f.write(']\n')
