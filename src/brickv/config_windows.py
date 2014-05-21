# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from brickv.config_common import *
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

def get_host_info_strings(count):
    host_info_strings = []

    for i in range(count):
        host_info_string = get_registry_value('HostInfo{0}'.format(i), None)

        if host_info_string is not None:
            host_info_strings.append(str(host_info_string))

    return host_info_strings

def set_host_info_strings(host_info_strings):
    i = 0

    for host_info_string in host_info_strings:
        set_registry_value('HostInfo{0}'.format(i), winreg.REG_SZ, str(host_info_string))
        i += 1

def legacy_get_host():
    return get_registry_value('Host', DEFAULT_HOST)

def legacy_set_host(host):
    set_registry_value('Host', winreg.REG_SZ, str(host))

def legacy_get_host_history(size):
    history = []

    for i in range(size):
        host = get_registry_value('HostHistory{0}'.format(i), None)

        if host is not None:
            history.append(str(host))

    return history

def legacy_set_host_history(history):
    i = 0

    for host in history:
        set_registry_value('HostHistory{0}'.format(i), winreg.REG_SZ, str(host))
        i += 1

def legacy_get_port():
    return int(get_registry_value('Port', DEFAULT_PORT))

def legacy_set_port(port):
    set_registry_value('Port', winreg.REG_DWORD, int(port))

def legacy_get_use_authentication():
    if DEFAULT_USE_AUTHENTICATION:
        default = 1
    else:
        default = 0

    value = get_registry_value('UseAuthentication', default)

    if value == 1:
        return True
    elif value == 0:
        return False
    else:
        return default

def legacy_set_use_authentication(use):
    set_registry_value('UseAuthentication', winreg.REG_DWORD, int(bool(use)))

def legacy_get_secret():
    return get_registry_value('Secret', DEFAULT_SECRET)

def legacy_set_secret(secret):
    set_registry_value('Secret', winreg.REG_SZ, str(secret))

def legacy_get_remember_secret():
    if DEFAULT_REMEMBER_SECRET:
        default = 1
    else:
        default = 0

    value = get_registry_value('RememberSecret', default)

    if value == 1:
        return True
    elif value == 0:
        return False
    else:
        return default

def legacy_set_remember_secret(remember):
    set_registry_value('RememberSecret', winreg.REG_DWORD, int(bool(remember)))
