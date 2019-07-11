# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014, 2017 Matthias Bolte <matthias@tinkerforge.com>

config_macos.py: Config Handling for macOS

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

import plistlib
import os
import subprocess

from brickv.config_common import *

CONFIG_FILENAME = os.path.expanduser('~/Library/Preferences/com.tinkerforge.brickv.plist')
CONFIG_DIRNAME = os.path.dirname(CONFIG_FILENAME)

def get_plist_value(name, default):
    if not os.path.exists(CONFIG_FILENAME):
        return default

    try:
        subprocess.call(['plutil', '-convert', 'xml1', CONFIG_FILENAME])

        with open(CONFIG_FILENAME, 'rb') as f:
            return plistlib.load(f)[name]
    except:
        return default

def set_plist_value(name, value):
    root = {}

    if os.path.exists(CONFIG_FILENAME):
        try:
            subprocess.call(['plutil', '-convert', 'xml1', CONFIG_FILENAME])

            with open(CONFIG_FILENAME, 'rb') as f:
                root = plistlib.load(f)
        except:
            pass

    root[name] = value

    if not os.path.exists(CONFIG_DIRNAME):
        os.makedirs(CONFIG_DIRNAME)

    with open(CONFIG_FILENAME, 'wb') as f:
        plistlib.dump(root, f)

def get_host_info_strings(max_count):
    strings = []

    try:
        count = int(get_plist_value('HostInfoCount', '-1'))
    except (ValueError, TypeError):
        count = max_count

    if count < 0 or count > max_count:
        count = max_count

    for i in range(count):
        string = get_plist_value('HostInfo{0}'.format(i), None)

        if string is not None:
            strings.append(str(string))

    return strings

def set_host_info_strings(strings):
    i = 0

    for string in strings:
        set_plist_value('HostInfo{0}'.format(i), str(string))
        i += 1

    set_plist_value('HostInfoCount', str(i))

def get_use_fusion_gui_style():
    return get_plist_value('UseFusionGUIStyle', str(DEFAULT_USE_FUSION_GUI_STYLE).lower()) == 'true'

def set_use_fusion_gui_style(value):
    set_plist_value('UseFusionGUIStyle', str(bool(value)).lower())

def get_auto_search_for_updates():
    return get_plist_value('AutoSearchForUpdates', str(DEFAULT_AUTO_SEARCH_FOR_UPDATES).lower()) == 'true'

def set_auto_search_for_updates(value):
    set_plist_value('AutoSearchForUpdates', str(bool(value)).lower())

def legacy_get_host():
    return get_plist_value('Host', DEFAULT_HOST)

def legacy_set_host(host):
    set_plist_value('Host', host)

def legacy_get_host_history(size):
    history = []

    for i in range(size):
        host = get_plist_value('HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(str(host))

    return history

def legacy_set_host_history(history):
    i = 0

    for host in history:
        set_plist_value('HostHistory{0}'.format(i), str(host))
        i += 1

def legacy_get_port():
    return int(get_plist_value('Port', DEFAULT_PORT))

def legacy_set_port(port):
    set_plist_value('Port', str(port))

def legacy_get_use_authentication():
    value = get_plist_value('UseAuthentication', str(DEFAULT_USE_AUTHENTICATION)).lower()

    if value == 'true':
        return True

    if value == 'false':
        return False

    return DEFAULT_USE_AUTHENTICATION

def legacy_set_use_authentication(use):
    set_plist_value('UseAuthentication', str(bool(use)))

def legacy_get_secret():
    return get_plist_value('Secret', DEFAULT_SECRET)

def legacy_set_secret(secret):
    set_plist_value('Secret', str(secret))

def legacy_get_remember_secret():
    value = get_plist_value('RememberSecret', str(DEFAULT_REMEMBER_SECRET)).lower()

    if value == 'true':
        return True

    if value == 'false':
        return False

    return DEFAULT_REMEMBER_SECRET

def legacy_set_remember_secret(remember):
    set_plist_value('RememberSecret', str(bool(remember)))
