#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
if (sys.hexversion & 0xFF000000) != 0x03000000:
    print('Python 3.x required')
    sys.exit(1)

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

cwd = os.getcwd()
basedir = os.path.dirname(__file__)
brickv = os.path.join(basedir, 'brickv')
for dirpath, dirnames, filenames in os.walk(brickv):
    if 'build_extra.py' in filenames:
        print('calling build_extra.py in ' + os.path.relpath(dirpath, basedir))
        os.chdir(dirpath)
        system(sys.executable + ' build_extra.py')
        os.chdir(cwd)
    if os.path.basename(dirpath) != 'ui':
        continue
    for filename in filenames:
        name, ext = os.path.splitext(filename)

        if ext != '.ui':
            continue
        out_file = os.path.normpath(os.path.join(dirpath, "..", "ui_" + name + ".py"))
        in_file = os.path.join(dirpath, filename)
        print('building ' + os.path.relpath(in_file, basedir))
        system(sys.executable + " pyuic5-fixed.py -o " + out_file + " " + in_file)

args = ' '.join(sys.argv[1:])
print('calling build_plugin_list.py ' + args)
os.chdir(cwd)
system(sys.executable + ' build_plugin_list.py ' + args)
