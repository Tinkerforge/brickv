# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012-2015, 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014, 2017 Matthias Bolte <matthias@tinkerforge.com>

infos.py: Common information structures for Tools/Bricks/Bricklets

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

from collections import namedtuple

from PyQt5.QtWidgets import QApplication

from brickv import config

UID_BRICKV = '$BRICKV'
UID_BRICKD = '$BRICKD'

class AbstractInfo:
    type = 'abstract'
    url_part = ''
    error = ''
    name = ''
    firmware_version_installed = (0, 0, 0)
    firmware_version_latest = (0, 0, 0)
    can_have_extension = False

class FirmwareInfo(AbstractInfo):
    type = 'firmware'

class PluginInfo(AbstractInfo):
    type = 'plugin'

class ExtensionFirmwareInfo(AbstractInfo):
    type = 'extension_firmware'

class ToolInfo(AbstractInfo):
    type = 'tool'

    def __repr__(self):
        return """{0}:
  version installed: {1},
  version latest: {2},
  url_part: {3}
""".format(self.name, self.firmware_version_installed,
           self.firmware_version_latest, self.url_part)

class ExtensionInfo(AbstractInfo):
    type = 'extension'
    name = 'Unknown'
    extension_type = -1
    position = ''
    master_info = None

    def __repr__(self):
        return self.name

    def get_combo_item(self):
        version_str = get_version_string(self.firmware_version_installed)
        master_version_str = get_version_string(self.master_info.firmware_version_installed)

        return '{0} ({1}) @ {2} [{3}] ({4})'.format(self.name,
                                                    version_str,
                                                    self.master_info.name,
                                                    self.master_info.uid,
                                                    master_version_str)

class DeviceInfo(AbstractInfo):
    uid = ''
    connected_uid = ''
    position = ''
    hardware_version = (0, 0, 0)
    device_identifier = 0
    plugin = None
    tab_window = None
    tab_index = -1
    enumeration_type = -1
    reverse_connection = None
    flashable_like_bricklet = False

    def __init__(self, connections=None):
        self.connections = connections or []
        self.bricklet_ports = tuple()

    def __repr__(self):
        repr_str = """{0} ({1}):
  connected UID: {2},
  position: {3},
  fw version installed: {4},
  fw version latest: {5},
  hw version: {6},
  device identifier: {7},
  url_part: {8},
  plugin: {9},
  tab_window: {10}
""".format(self.name, self.uid, self.connected_uid, self.position,
           self.firmware_version_installed, self.firmware_version_latest,
           self.hardware_version, self.device_identifier,
           self.url_part, self.plugin, self.tab_window)

        if len(self.connections) > 0:
            repr_str += "  Connections:\n"
            for port, con in self.connections:
                repr_str += "   {0}: {1} ({2})\n".format(port, con.name, con.uid)
        return repr_str

    def get_combo_item(self):
        version_str = get_version_string(self.firmware_version_installed)

        return '{0} [{1}] ({2})'.format(self.name, self.uid, version_str)

    def connections_keys(self):
        return [k for k, v in self.connections]

    def connections_values(self):
        return [v for k, v in self.connections]

    def connections_get(self, key):
        result = [v for k, v in self.connections if k == key]
        if key != '0':
            assert len(result) <= 1, 'On a port, other than the "meta" port 0 (that is used for extensions),'\
                ' there should only be one device attached. On port {} there where {} devices attached: {}'\
                .format(key, len(result), [r.uid for r in result])
        return result

class BrickletInfo(DeviceInfo):
    type = 'bricklet'
    flashable_like_bricklet = True

class BrickInfo(DeviceInfo):
    can_have_extension = False
    type = 'brick'
    flashable_like_bricklet = False

    def __init__(self):
        super().__init__()

        self.bricklet_ports = ('a', 'b')

class BrickHATInfo(BrickInfo):
    flashable_like_bricklet = True
    def __init__(self):
        super().__init__()
        self.bricklet_ports = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')

class BrickHATZeroInfo(BrickInfo):
    flashable_like_bricklet = True
    def __init__(self):
        super().__init__()
        self.bricklet_ports = ('a', 'b', 'c', 'd')

class BrickMasterInfo(BrickInfo):
    can_have_extension = True
    connection_type = None

    def __init__(self):
        super().__init__()

        self.bricklet_ports = ('a', 'b', 'c', 'd')
        self.extensions = {'ext0': None, 'ext1': None}

class BrickletIsolatorInfo(BrickletInfo):
    def __init__(self):
        super().__init__()
        self.bricklet_ports = {'z'}


class BrickREDInfo(BrickInfo):
    def __init__(self):
        super().__init__()
        self.bindings_infos = []
        self.brickv_info = ToolInfo()
        self.brickv_info.name = "Brick Viewer"

def get_bindings_name(url_part):
    # These are all bindings supported on the red brick.
    url_to_name = {'c': 'C/C++ Bindings',
                   'csharp': 'C#/Mono Bindings',
                   'delphi': 'Delphi/Lazarus Bindings',
                   'java': 'Java Bindings',
                   'javascript': 'JavaScript Bindings',
                   'matlab': 'Octave Bindings',
                   'perl': 'Perl Bindings',
                   'php': 'PHP Bindings',
                   'python': 'Python Bindings',
                   'ruby': 'Ruby Bindings',
                   'shell': 'Shell Bindings',
                   'vbnet': 'VB.NET Bindings'}

    return url_to_name.get(url_part, None)

class BindingInfo(AbstractInfo):
    type = 'binding'

    def __repr__(self):
        return """{0}:
version installed: {1},
version latest: {2},
url_part: {3}
""".format(self.name, self.firmware_version_installed,
           self.firmware_version_latest, self.url_part)

def get_version_string(version_tuple, replace_unknown=None, is_red_brick=False):
    if replace_unknown is not None and version_tuple == (0, 0, 0):
        return replace_unknown
    return '.'.join(map(str, version_tuple if not is_red_brick else version_tuple[:-1]))

if not '_infos' in globals():
    _infos = {UID_BRICKV: ToolInfo(), UID_BRICKD: ToolInfo()}
    _infos[UID_BRICKV].name = 'Brick Viewer'
    _infos[UID_BRICKV].firmware_version_installed = tuple(map(int, config.BRICKV_VERSION.split('.')))
    _infos[UID_BRICKD].name = 'Brick Daemon'

LatestFirmwares = namedtuple('LatestFirmwares', ['tool_infos', 'firmware_infos', 'plugin_infos',
                                                 'extension_firmware_infos', 'red_image_infos', 'binding_infos'])

if not '_latest_fws' in globals():
    _latest_fws = LatestFirmwares({}, {}, {}, {}, {}, {})


def get_latest_fw(info):
    if isinstance(info, BrickREDInfo):
        if 'full' not in _latest_fws.red_image_infos:
            latest_fw = (0, 0, 0)
        else:
            latest_fw = _latest_fws.red_image_infos['full'].firmware_version_latest
        return latest_fw
    elif info.type == 'brick':
        d = _latest_fws.firmware_infos
    elif info.type == 'bricklet':
        d = _latest_fws.plugin_infos
    elif info.type == 'extension':
        d = _latest_fws.extension_firmware_infos
    elif info.type == 'tool':
        name_to_url_part = {'Brick Viewer': 'brickv', 'Brick Daemon': 'brickd'}
        if info.name not in name_to_url_part.keys():
            raise Exception("The name -> url_part mapping was incomplete: " + info.name)
        info.url_part = name_to_url_part[info.name]
        d = _latest_fws.tool_infos
    elif info.type == 'binding':
        d = _latest_fws.binding_infos
    else:
        raise Exception("Unexpected info type " + info.type)

    if info.url_part not in d:
        return (0, 0, 0)
    else:
        return d[info.url_part].firmware_version_latest

def add_latest_fw(info):
    latest_fw = get_latest_fw(info)

    version_changed = info.firmware_version_latest != latest_fw
    info.firmware_version_latest = latest_fw

    # RED Brick: Add latest binding and brickv versions
    if isinstance(info, BrickREDInfo):
        d = _latest_fws.binding_infos
        for binding_info in info.bindings_infos:
            if binding_info.url_part not in d:
                latest_fw = (0, 0, 0)
            else:
                latest_fw = d[binding_info.url_part].firmware_version_latest

            version_changed |= binding_info.firmware_version_latest != latest_fw
            binding_info.firmware_version_latest = latest_fw

        d = _latest_fws.tool_infos
        if info.brickv_info.url_part not in d:
            latest_fw = (0, 0, 0)
        else:
            latest_fw = d[info.brickv_info.url_part].firmware_version_latest

        version_changed |= info.brickv_info.firmware_version_latest != latest_fw
        info.brickv_info.firmware_version_latest = latest_fw

    # Add latest extension versions
    if info.can_have_extension:
        d = _latest_fws.extension_firmware_infos
        for extension in info.extensions.values():
            if extension is None:
                continue

            if extension.url_part not in d:
                latest_fw = (0, 0, 0)
            else:
                latest_fw = d[extension.url_part].firmware_version_latest
            version_changed |= extension.firmware_version_latest != latest_fw
            extension.firmware_version_latest = latest_fw

    return version_changed

def add_info(info):
    add_latest_fw(info)

    _infos[info.uid] = info
    get_infos_changed_signal().emit(info.uid)

def remove_info(uid):
    _infos.pop(uid)
    get_infos_changed_signal().emit(uid)

def update_info(uid):
    info = _infos.get(uid)
    if info is not None:
        add_latest_fw(info)

    get_infos_changed_signal().emit(uid)

def get_info(uid):
    try:
        return _infos[uid]
    except KeyError:
        return None

def reset_latest_fws():
    update_latest_fws(LatestFirmwares({}, {}, {}, {}, {}, {}))

def update_latest_fws(latest_fws):
    global _latest_fws
    _latest_fws = latest_fws

    for uid, info in _infos.items():
        latest_fw_changed = add_latest_fw(info)
        if latest_fw_changed:
            get_infos_changed_signal().emit(uid)

def get_infos():
    return sorted(_infos.values(), key=lambda x: x.name)

def get_latest_fws():
    return _latest_fws

def get_device_infos():
    return sorted([info for info in _infos.values() if info.type == 'brick' or info.type == 'bricklet'], key=lambda x: x.name)

def get_brick_infos():
    return sorted([info for info in _infos.values() if info.type == 'brick'], key=lambda x: x.name)

def get_bricklet_infos():
    return sorted([info for info in _infos.values() if info.type == 'bricklet'], key=lambda x: x.name)

def get_extension_infos():
    extension_infos = []

    for brick_info in get_brick_infos():
        if brick_info.can_have_extension:
            extension_infos += list(filter(lambda value: value != None, brick_info.extensions.values()))

    return sorted(extension_infos, key=lambda x: x.name)

def get_infos_changed_signal():
    return QApplication.instance().infos_changed_signal
