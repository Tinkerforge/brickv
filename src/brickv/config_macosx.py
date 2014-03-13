# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from brickv.config_common import *
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
    set_plist_value('Host', host)

def get_host_history(size):
    history = []

    for i in range(size):
        host = get_plist_value('HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(str(host))

    return history

def set_host_history(history):
    i = 0

    for host in history:
        set_plist_value('HostHistory{0}'.format(i), str(host))
        i += 1

def get_port():
    return int(get_plist_value('Port', DEFAULT_PORT))

def set_port(port):
    set_plist_value('Port', str(port))

def get_use_authentication():
    value = get_plist_value('UseAuthentication', str(DEFAULT_USE_AUTHENTICATION)).lower()

    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return DEFAULT_USE_AUTHENTICATION

def set_use_authentication(use):
    set_plist_value('UseAuthentication', str(bool(use)))

def get_secret():
    return get_plist_value('Secret', DEFAULT_SECRET)

def set_secret(secret):
    set_plist_value('Secret', str(secret))

def get_remember_secret():
    value = get_plist_value('RememberSecret', str(DEFAULT_REMEMBER_SECRET)).lower()

    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return DEFAULT_REMEMBER_SECRET

def set_remember_secret(remember):
    set_plist_value('RememberSecret', str(bool(remember)))
