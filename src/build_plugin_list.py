#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

build_plugin_list.py: Collects Brick Viewer plugins into a list

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
if (sys.hexversion & 0xFF000000) != 0x02000000:
    print 'Python 2.x required'
    sys.exit(1)

import os

released_only = False

if len(sys.argv) > 1:
    if sys.argv[1] == 'release':
        released_only = True
    else:
        raise Exception('Unexpected argument ' + sys.argv[1])

imports = []
device_classes = []
root = os.path.abspath(__file__).replace(__file__, '')
plugins = os.path.join(root, 'brickv', 'plugin_system', 'plugins')
bindings = os.path.join(root, 'brickv', 'bindings')

for plugin in sorted(os.listdir(plugins)):
    if not os.path.isfile(os.path.join(plugins, plugin, '__init__.py')):
        continue

    brick_binding = os.path.join(bindings, 'brick_{0}.py'.format(plugin))
    bricklet_binding = os.path.join(bindings, 'bricklet_{0}.py'.format(plugin))

    if os.path.isfile(brick_binding):
        if released_only:
            with open(brick_binding, 'r') as f:
                if '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read():
                    continue
    elif os.path.isfile(bricklet_binding):
        if released_only:
            with open(bricklet_binding, 'r') as f:
                if '#### __DEVICE_IS_NOT_RELEASED__ ####' in f.read():
                    continue
    else:
        raise Exception('No bindings found corresponding to plugin ' + plugin)

    imports.append('from brickv.plugin_system.plugins.{0} import device_class as {0}\n'.format(plugin))
    device_classes.append('    {0},\n'.format(plugin))

with open(os.path.join(plugins, '__init__.py'), 'wb') as f:
    f.writelines(map(lambda s: s.encode('utf-8'), imports))
    f.write(b'\n')
    f.write(b'device_classes = [\n')
    f.writelines(map(lambda s: s.encode('utf-8'), device_classes))
    f.write(b']\n')
