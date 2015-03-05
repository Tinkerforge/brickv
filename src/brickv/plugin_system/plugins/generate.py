#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

imports = []
device_classes = []

for plugin in sorted(os.listdir('.')):
    if not os.path.isdir(os.path.join('.', plugin)):
        continue

    imports.append('from brickv.plugin_system.plugins.{0} import device_class as {0}\n'.format(plugin))
    device_classes.append('    {0},\n'.format(plugin))

f = open('__init__.py', 'wb')
if sys.version_info >= (3, 0):
    f.writelines(map(lambda s: bytes(s, 'UTF-8'), imports))
    f.write(b'\n')
    f.write(b'device_classes = [\n')
    f.writelines(map(lambda s: bytes(s, 'UTF-8'), device_classes))
    f.write(b']\n')
else:
    f.writelines(imports)
    f.write('\n')
    f.write('device_classes = [\n')
    f.writelines(device_classes)
    f.write(']\n')
