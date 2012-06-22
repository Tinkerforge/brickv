# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

config_macosx.py: Config Handling for Mac OSX

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

from config import *
import plistlib
import os
import subprocess

CONFIG_FILENAME = os.path.expanduser('~/Library/Preferences/com.tinkerforge.brickv.plist')
CONFIG_DIRNAME = os.path.dirname(CONFIG_FILENAME)

def get_plist_value(name, default):
    try:
        subprocess.call(['plutil', '-convert', 'xml1', CONFIG_FILENAME])
        root = plistlib.readPlist(CONFIG_FILENAME)
        return root[name]
    except:
        return default

def set_plist_value(name, value):
    try:
        subprocess.call(['plutil', '-convert', 'xml1', CONFIG_FILENAME])
        root = plistlib.readPlist(CONFIG_FILENAME)
    except:
        root = {}
    root[name] = value
    if not os.path.exists(CONFIG_DIRNAME):
        os.makedirs(CONFIG_DIRNAME)
    plistlib.writePlist(root, CONFIG_FILENAME)

def get_host():
    return get_plist_value('Host', DEFAULT_HOST)

def set_host(host):
    return set_plist_value('Host', host)

def get_port():
    return int(get_plist_value('Port', DEFAULT_PORT))

def set_port(port):
    return set_plist_value('Port', str(port))
