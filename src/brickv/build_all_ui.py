#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

file_url = os.path.abspath( __file__ ).replace(__file__, '')
for f in os.walk(file_url):
    if 'build_ui.py' in f[2]:
        print 'building ' + f[0]
        os.chdir(f[0])
        os.system('python build_ui.py')
