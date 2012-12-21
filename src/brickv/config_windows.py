# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

config_windows.py: Config Handling for Windows

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

from config_common import *
import _winreg as winreg

KEY_NAME = 'Software\\Tinkerforge\\Brickv'

def get_registry_value(name, default):
    try:
        reg = winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY_NAME)
    except WindowsError:
        return default
    else:
        try:
            return winreg.QueryValueEx(reg, name)[0]
        except:
            return default
        finally:
            winreg.CloseKey(reg)

def set_registry_value(name, type, value):
    try:
        reg = winreg.CreateKey(winreg.HKEY_CURRENT_USER, KEY_NAME)
    except WindowsError:
        logging.warn('Could not create registry key: HKCU\\{0}'.format(KEY_NAME))
    else:
        try:
            winreg.SetValueEx(reg, name, 0, type, value)
        except:
            logging.warn('Could not set registry value: HKCU\\{0}\\{1}'.format(KEY_NAME, name))
        finally:
            winreg.CloseKey(reg)

def get_host():
    return get_registry_value('Host', DEFAULT_HOST)

def set_host(host):
    set_registry_value('Host', winreg.REG_SZ, host)

def get_host_history(size):
    history = []

    for i in range(size):
        host = get_registry_value('HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(host)

    return history

def set_host_history(history):
    i = 0

    for host in history:
        set_registry_value('HostHistory{0}'.format(i), winreg.REG_SZ, host)
        i += 1

def get_port():
    return int(get_registry_value('Port', DEFAULT_PORT))

def set_port(port):
    set_registry_value('Port', winreg.REG_DWORD, port)
