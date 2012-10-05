# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

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

from config import *
import ConfigParser
import os

XDG_CONFIG_HOME = os.getenv('XDG_CONFIG_HOME')

if XDG_CONFIG_HOME is None or len(XDG_CONFIG_HOME) < 1:
    CONFIG_FILENAME = os.path.expanduser('~/.config/Tinkerforge/brickv.conf')
else:
    CONFIG_FILENAME = os.path.join(XDG_CONFIG_HOME, 'Tinkerforge/brickv.conf')

CONFIG_DIRNAME = os.path.dirname(CONFIG_FILENAME)

def get_config_value(section, option, default):
    scp = ConfigParser.SafeConfigParser()
    scp.read(CONFIG_FILENAME)
    try:
        return scp.get(section, option)
    except ConfigParser.Error:
        return default

def set_config_value(section, option, value):
    scp = ConfigParser.SafeConfigParser()
    scp.read(CONFIG_FILENAME)
    if not scp.has_section(section):
        scp.add_section(section)
    scp.set(section, option, value)
    if not os.path.exists(CONFIG_DIRNAME):
        os.makedirs(CONFIG_DIRNAME)
    scp.write(file(CONFIG_FILENAME, 'wb'))

def get_host():
    return get_config_value('Connection', 'Host', DEFAULT_HOST)

def set_host(host):
    set_config_value('Connection', 'Host', host)

def get_host_history(size):
    history = []

    for i in range(size):
        host = get_config_value('Connection', 'HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(host)

    return history

def set_host_history(history):
    i = 0

    for host in history:
        set_config_value('Connection', 'HostHistory{0}'.format(i), host)
        i += 1

def get_port():
    return int(get_config_value('Connection', 'Port', str(DEFAULT_PORT)))

def set_port(port):
    set_config_value('Connection', 'Port', str(port))
