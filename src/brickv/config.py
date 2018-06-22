# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Matthias Bolte <matthias@tinkerforge.com>

config.py: Config Handling

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

import sys
from brickv.config_common import *

class HostInfo(object):
    host = DEFAULT_HOST
    port = DEFAULT_PORT
    use_authentication = DEFAULT_USE_AUTHENTICATION
    secret = DEFAULT_SECRET
    remember_secret = DEFAULT_REMEMBER_SECRET

    def duplicate(self):
        host_info = HostInfo()

        host_info.host = self.host
        host_info.port = self.port
        host_info.use_authentication = self.use_authentication
        host_info.secret = self.secret
        host_info.remember_secret = self.remember_secret

        return host_info

def get_host_info_strings():
    return [DEFAULT_HOST_INFO]

def set_host_info_strings(host_info_strings):
    pass

def legacy_get_host():
    return DEFAULT_HOST

def legacy_set_host(host):
    pass

def legacy_get_host_history(size):
    return []

def legacy_set_host_history(history):
    pass

def legacy_get_port():
    return DEFAULT_PORT

def legacy_set_port(port):
    pass

def legacy_get_use_authentication():
    return DEFAULT_USE_AUTHENTICATION

def legacy_set_use_authentication(use):
    pass

def legacy_get_secret():
    return DEFAULT_SECRET

def legacy_set_secret(secret):
    pass

def legacy_get_remember_secret():
    return DEFAULT_REMEMBER_SECRET

def legacy_set_remember_secret(remember):
    pass

if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
    from brickv.config_linux import *
elif sys.platform == 'darwin':
    from brickv.config_macos import *
elif sys.platform == 'win32':
    from brickv.config_windows import *
else:
    print("Unsupported platform: " + sys.platform)

def get_host_infos(count):
    host_infos = []

    for host_info_string in get_host_info_strings(count):
        # host|port|use_authentication|remember_secret|secret
        parts = host_info_string.split('|', 5)

        if len(parts) != 5:
            continue

        try:
            host_info = HostInfo()
            host_info.host = parts[0]
            host_info.port = int(parts[1])
            host_info.use_authentication = bool(int(parts[2]))
            host_info.secret = parts[4]
            host_info.remember_secret = bool(int(parts[3]))

            if not host_info.remember_secret:
                host_info.secret = DEFAULT_SECRET

            host_infos.append(host_info)
        except:
            continue

        if len(host_infos) == count:
            break

    if len(host_infos) == 0:
        host_info = HostInfo()

        host_info.host = legacy_get_host()
        host_info.port = legacy_get_port()
        host_info.use_authentication = legacy_get_use_authentication()
        host_info.secret = legacy_get_secret()
        host_info.remember_secret = legacy_get_remember_secret()

        host_infos.append(host_info)

        if len(host_infos) < count:
            for host in legacy_get_host_history(HOST_INFO_COUNT):
                host_info = HostInfo()

                host_info.host = host
                host_info.port = legacy_get_port()
                host_info.use_authentication = legacy_get_use_authentication()
                host_info.secret = legacy_get_secret()
                host_info.remember_secret = legacy_get_remember_secret()

                if not host_info.remember_secret:
                    host_info.secret = DEFAULT_SECRET

                host_infos.append(host_info)

                if len(host_infos) == count:
                    break

    return host_infos

def set_host_infos(host_infos):
    host_info_strings = []

    for host_info in host_infos:
        use_authentication = 0
        remember_secret = 0
        secret = DEFAULT_SECRET

        if host_info.use_authentication:
            use_authentication = 1

        if host_info.remember_secret:
            remember_secret = 1
            secret = host_info.secret

        # host|port|use_authentication|remember_secret|secret
        host_info_string = '{0}|{1}|{2}|{3}|{4}'.format(host_info.host,
                                                        host_info.port,
                                                        use_authentication,
                                                        remember_secret,
                                                        secret)

        host_info_strings.append(host_info_string)

    set_host_info_strings(host_info_strings)

    if len(host_infos) > 0:
        legacy_set_host(host_infos[0].host)
        legacy_set_port(host_infos[0].port)
        legacy_set_use_authentication(host_infos[0].use_authentication)

        if host_infos[0].remember_secret:
            legacy_set_secret(host_infos[0].secret)
        else:
            legacy_set_secret(DEFAULT_SECRET)

        legacy_set_remember_secret(host_infos[0].remember_secret)

        host_history = []

        for host_info in host_infos[1:]:
            host_history.append(host_info.host)

        legacy_set_host_history(host_history)
