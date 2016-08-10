#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
if (sys.hexversion & 0xFF000000) != 0x02000000:
    print 'Python 2.x required'
    sys.exit(1)

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

cwd = os.getcwd()
brickv = os.path.join(os.path.abspath(__file__).replace(__file__, ''), 'brickv')
for f in os.walk(brickv):
    if 'build_ui.py' in f[2]:
        print('building ' + f[0])
        os.chdir(f[0])
        system('python build_ui.py')

args = ' '.join(sys.argv[1:])
print('calling build_plugin_list.py ' + args)
os.chdir(cwd)
system('python build_plugin_list.py ' + args)
