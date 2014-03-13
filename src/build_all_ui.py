#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

brickv = os.path.join(os.path.abspath(__file__).replace(__file__, ''), 'brickv')
for f in os.walk(brickv):
    if 'build_ui.py' in f[2]:
        print 'building ' + f[0]
        os.chdir(f[0])
        os.system('python build_ui.py')

p = os.path.join(brickv, 'plugin_system', 'plugins')
print 'calling ' +  p + '/generate.py'
os.chdir(p)
os.system('python generate.py')
