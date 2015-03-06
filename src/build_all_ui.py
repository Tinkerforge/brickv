#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

cwd = os.getcwd()
brickv = os.path.join(os.path.abspath(__file__).replace(__file__, ''), 'brickv')
for f in os.walk(brickv):
    if 'build_ui.py' in f[2]:
        print('building ' + f[0])
        os.chdir(f[0])
        os.system('python build_ui.py')

args = ' '.join(sys.argv[1:])
print('calling build_plugin_list.py ' + args)
os.chdir(cwd)
os.system('python build_plugin_list.py ' + args)
