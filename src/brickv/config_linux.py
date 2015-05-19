# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Matthias Bolte <matthias@tinkerforge.com>

config_linux.py: Config Handling for Linux

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
import os

try:
    import configparser
except:
    import ConfigParser as configparser # Python 2 fallback

XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME')

if XDG_CONFIG_HOME is None or len(XDG_CONFIG_HOME) < 1:
    CONFIG_FILENAME = os.path.expanduser('~/.config/Tinkerforge/brickv.conf')
else:
    CONFIG_FILENAME = os.path.join(XDG_CONFIG_HOME, 'Tinkerforge/brickv.conf')

CONFIG_DIRNAME = os.path.dirname(CONFIG_FILENAME)

def get_config_value(section, option, default):
    scp = configparser.SafeConfigParser()
    scp.read(CONFIG_FILENAME)

    try:
        return scp.get(section, option)
    except configparser.Error:
        return default

def set_config_value(section, option, value):
    scp = configparser.SafeConfigParser()
    scp.read(CONFIG_FILENAME)

    if not scp.has_section(section):
        scp.add_section(section)

    scp.set(section, option, value)

    if not os.path.exists(CONFIG_DIRNAME):
        os.makedirs(CONFIG_DIRNAME)

    with open(CONFIG_FILENAME, 'wb') as f:
        scp.write(f)

def get_host_info_strings(max_count):
    strings = []

    try:
        count = int(get_config_value('Connection', 'HostInfoCount', '-1'))
    except:
        count = max_count

    if count < 0 or count > max_count:
        count = max_count

    for i in range(count):
        string = get_config_value('Connection', 'HostInfo{0}'.format(i), None)

        if string != None:
            strings.append(str(string))

    return strings

def set_host_info_strings(strings):
    i = 0

    for string in strings:
        set_config_value('Connection', 'HostInfo{0}'.format(i), str(string))
        i += 1

    set_config_value('Connection', 'HostInfoCount', str(i))

def legacy_get_host():
    return get_config_value('Connection', 'Host', DEFAULT_HOST)

def legacy_set_host(host):
    set_config_value('Connection', 'Host', str(host))

def legacy_get_host_history(size):
    history = []

    for i in range(size):
        host = get_config_value('Connection', 'HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(str(host))

    return history

def legacy_set_host_history(history):
    i = 0

    for host in history:
        set_config_value('Connection', 'HostHistory{0}'.format(i), str(host))
        i += 1

def legacy_get_port():
    return int(get_config_value('Connection', 'Port', str(DEFAULT_PORT)))

def legacy_set_port(port):
    set_config_value('Connection', 'Port', str(int(port)))

def legacy_get_use_authentication():
    value = get_config_value('Authentication', 'UseAuthentication', str(DEFAULT_USE_AUTHENTICATION)).lower()

    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return DEFAULT_USE_AUTHENTICATION

def legacy_set_use_authentication(use):
    set_config_value('Authentication', 'UseAuthentication', str(bool(use)))

def legacy_get_secret():
    return get_config_value('Authentication', 'Secret', DEFAULT_SECRET)

def legacy_set_secret(secret):
    set_config_value('Authentication', 'Secret', str(secret))

def legacy_get_remember_secret():
    value = get_config_value('Authentication', 'RememberSecret', str(DEFAULT_REMEMBER_SECRET)).lower()

    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return DEFAULT_REMEMBER_SECRET

def legacy_set_remember_secret(remember):
    set_config_value('Authentication', 'RememberSecret', str(bool(remember)))
