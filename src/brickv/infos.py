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

def get_version_string(version_tuple, replace_unknown=None, is_red_brick=False):
    if replace_unknown is not None and version_tuple == (0, 0, 0):
        return replace_unknown

    return '.'.join(map(str, version_tuple if not is_red_brick else version_tuple[:-1]))

LatestFirmwares = namedtuple('LatestFirmwares', ['tool_infos', 'firmware_infos', 'plugin_infos',
                                                 'extension_firmware_infos', 'red_image_infos', 'bindings_infos'])

class AbstractInfo:
    changed = False
    kind = 'abstract'
    url_part = ''
    error = ''
    name = ''
    firmware_version_installed = (0, 0, 0)
    firmware_version_latest = (0, 0, 0)
    firmware_versions = None
    can_have_extension = False
    extensions = None

    def __init__(self):
        self.firmware_versions = []

    def __setattr__(self, name, value):
        if name == 'changed':
            if not isinstance(value, bool):
                raise TypeError('cannot set changed to non-bool value')

            if value == True:
                raise ValueError('cannot set changed to True')

            assert value == False

            object.__setattr__(self, 'changed', value)
            return

        if not hasattr(self, name):
            raise ValueError('unknown attribute: ' + name)

        old_value = getattr(self, name)

        object.__setattr__(self, name, value)

        if old_value != value:
            object.__setattr__(self, 'changed', True)

    def mark_as_changed(self):
        object.__setattr__(self, 'changed', True)

    def update_firmware_version_latest(self):
        latest_fw = inventory.get_latest_fw(self)

        version_changed = self.firmware_version_latest != latest_fw
        self.firmware_version_latest = latest_fw

        # RED Brick: Add latest binding and brickv versions
        if isinstance(self, BrickREDInfo):
            d = inventory._latest_fws.bindings_infos

            for bindings_info in self.bindings_infos:
                if bindings_info.url_part not in d:
                    latest_fw = (0, 0, 0)
                else:
                    latest_fw = d[bindings_info.url_part].firmware_version_latest

                version_changed |= bindings_info.firmware_version_latest != latest_fw
                bindings_info.firmware_version_latest = latest_fw

            d = inventory._latest_fws.tool_infos

            if self.brickv_info.url_part not in d:
                latest_fw = (0, 0, 0)
            else:
                latest_fw = d[self.brickv_info.url_part].firmware_version_latest

            version_changed |= self.brickv_info.firmware_version_latest != latest_fw
            self.brickv_info.firmware_version_latest = latest_fw

        # Add latest extension versions
        if self.can_have_extension:
            d = inventory._latest_fws.extension_firmware_infos

            for extension in self.extensions.values():
                if extension is None:
                    continue

                if extension.url_part not in d:
                    latest_fw = (0, 0, 0)
                else:
                    latest_fw = d[extension.url_part].firmware_version_latest

                version_changed |= extension.firmware_version_latest != latest_fw
                extension.firmware_version_latest = latest_fw

        return version_changed

class FirmwareInfo(AbstractInfo):
    kind = 'firmware'

class PluginInfo(AbstractInfo):
    kind = 'plugin'

class ExtensionFirmwareInfo(AbstractInfo):
    kind = 'extension_firmware'

class ToolInfo(AbstractInfo):
    kind = 'tool'

    def __repr__(self):
        return """{0}:
  version installed: {1},
  version latest: {2},
  url_part: {3}
""".format(self.name, self.firmware_version_installed,
           self.firmware_version_latest, self.url_part)

class ExtensionInfo(AbstractInfo):
    kind = 'extension'
    name = 'Unknown'
    extension_type = -1
    position = ''
    master_info = None

    def __repr__(self):
        return """{0}:
  fw version installed: {1},
  fw version latest: {2}""".format(self.name,
                                   self.firmware_version_installed,
                                   self.firmware_version_latest)

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
    flashable_like_bricklet = False
    reverse_connection = None
    _connections = None
    bricklet_ports = ()

    def __init__(self):
        super().__init__()

        self._connections = []

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

        if len(self._connections) > 0:
            repr_str += "  Connections:\n"

            for port, con in self._connections:
                repr_str += "   {0}: {1} ({2})\n".format(port, con.name, con.uid)

        return repr_str

    def get_combo_item(self):
        version_str = get_version_string(self.firmware_version_installed)

        return '{0} [{1}] ({2})'.format(self.name, self.uid, version_str)

    def connections_items(self):
        return list(self._connections)

    def connections_keys(self):
        return [k for k, v in self._connections]

    def connections_values(self):
        return [v for k, v in self._connections]

    def connections_get(self, key):
        result = [v for k, v in self._connections if k == key]

        return result

    def connections_add_item(self, item):
        result = len(self.connections_get(item[0])) > 0

        self._connections.append(item)
        self.mark_as_changed()

        return result

    def connections_remove_item(self, item):
        old_length = len(self._connections)

        self._connections.remove(item)

        if len(self._connections) != old_length:
            self.mark_as_changed()

    def connections_remove_value(self, value):
        old_length = len(self._connections)

        self._connections = [(k, v) for k, v in self._connections if v != value]

        if len(self._connections) != old_length:
            self.mark_as_changed()

class TNGInfo(DeviceInfo):
    kind = 'tng'
    flashable_like_bricklet = True

class BrickletInfo(DeviceInfo):
    kind = 'bricklet'
    flashable_like_bricklet = True

class BrickInfo(DeviceInfo):
    kind = 'brick'
    bricklet_ports = ('a', 'b')
    can_have_extension = False
    flashable_like_bricklet = False

class BrickHATInfo(BrickInfo):
    bricklet_ports = ('a', 'b', 'c', 'd', 'e', 'f', 'g', 'h')
    flashable_like_bricklet = True

class BrickHATZeroInfo(BrickInfo):
    bricklet_ports = ('a', 'b', 'c', 'd')
    flashable_like_bricklet = True

class BrickWithExtensions(BrickInfo):
    can_have_extension = True

    def __init__(self):
        super().__init__()

        self.extensions = {'ext0': None, 'ext1': None}

    def get_extension_info(self, extension_type):
        for ext_info in self.extensions.values():
            if ext_info is None:
                continue

            if ext_info.extension_type == extension_type:
                return ext_info

        return None

class BrickMasterInfo(BrickWithExtensions):
    bricklet_ports = ('a', 'b', 'c', 'd')
    connection_type = None

class BrickletIsolatorInfo(BrickletInfo):
    bricklet_ports = ('z')

class BrickESP32Info(BrickInfo):
    bricklet_ports = ('a', 'b', 'c', 'd', 'e', 'f')

class BrickESP32EthernetInfo(BrickInfo):
    bricklet_ports = ('a', 'b', 'c', 'd', 'e', 'f')

class BrickREDInfo(BrickWithExtensions):
    bricklet_ports = ()
    bindings_infos = None
    brickv_info = None

    def __init__(self):
        super().__init__()

        self.brickv_info = ToolInfo()
        self.brickv_info.name = "Brick Viewer"
        self.bindings_infos = []

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

class BindingsInfo(AbstractInfo):
    kind = 'bindings'

    def __repr__(self):
        return """{0}:
version installed: {1},
version latest: {2},
url_part: {3}
""".format(self.name, self.firmware_version_installed,
           self.firmware_version_latest, self.url_part)

class Inventory:
    def __init__(self):
        brickd_info = ToolInfo()
        brickd_info.name = 'Brick Daemon'

        brickv_info = ToolInfo()
        brickv_info.name = 'Brick Viewer'
        brickv_info.firmware_version_installed = tuple(map(int, config.BRICKV_VERSION.split('.')))

        self._infos = {UID_BRICKD: brickd_info, UID_BRICKV: brickv_info}

        self._latest_fws = LatestFirmwares({}, {}, {}, {}, {}, {})

        self.info_changed = QApplication.instance().info_changed_signal

    def add_info(self, info):
        self._infos[info.uid] = info
        self.info_changed.emit(info.uid)

    def remove_info(self, uid):
        info = self._infos.pop(uid)
        if isinstance(info, DeviceInfo):
            if info.reverse_connection is not None:
                info.reverse_connection.connections_remove_value(info)
            for connection in info.connections_values():
                connection.reverse_connection = None

        self.info_changed.emit(uid)

    def get_info(self, uid):
        try:
            return self._infos[uid]
        except KeyError:
            return None

    def get_infos(self):
        return sorted(self._infos.values(), key=lambda x: x.name)

    def get_device_infos(self):
        return sorted([info for info in self._infos.values() if info.kind == 'brick' or info.kind == 'bricklet' or info.kind == 'tng'], key=lambda x: x.name)

    def get_brick_infos(self):
        return sorted([info for info in self._infos.values() if info.kind == 'brick'], key=lambda x: x.name)

    def get_bricklet_infos(self):
        return sorted([info for info in self._infos.values() if info.kind == 'bricklet' or info.kind == 'tng'], key=lambda x: x.name)

    def get_extension_infos(self):
        extension_infos = []

        for brick_info in self.get_brick_infos():
            if brick_info.can_have_extension:
                extension_infos += list(filter(lambda value: value != None, brick_info.extensions.values()))

        return sorted(extension_infos, key=lambda x: x.name)

    def sync(self):
        for info in self._infos.values():
            if isinstance(info, BrickWithExtensions):
                for extension_info in info.extensions.values():
                    if extension_info != None and extension_info.changed:
                        extension_info.changed = False
                        info.mark_as_changed()

            if info.changed:
                info.changed = False

                if hasattr(info, 'uid'):
                    self.info_changed.emit(info.uid)

    def get_latest_fw(self, info):
        if isinstance(info, BrickREDInfo):
            if 'full' not in self._latest_fws.red_image_infos:
                latest_fw = (0, 0, 0)
            else:
                latest_fw = self._latest_fws.red_image_infos['full'].firmware_version_latest

            return latest_fw
        elif info.kind == 'brick' and not info.flashable_like_bricklet:
            d = self._latest_fws.firmware_infos
        elif info.kind == 'bricklet' or (info.kind == 'brick' and info.flashable_like_bricklet):
            d = self._latest_fws.plugin_infos
        elif info.kind == 'extension':
            d = self._latest_fws.extension_firmware_infos
        elif info.kind == 'tool':
            name_to_url_part = {'Brick Viewer': 'brickv', 'Brick Daemon': 'brickd'}

            if info.name not in name_to_url_part.keys():
                raise Exception("The name -> url_part mapping was incomplete: " + info.name)

            info.url_part = name_to_url_part[info.name]
            d = self._latest_fws.tool_infos
        elif info.kind == 'bindings':
            d = self._latest_fws.bindings_infos
        elif info.kind == 'tng':
            return (0, 0, 0) # TODO: Implement me!
        else:
            raise Exception("Unexpected info kind " + info.kind)

        if info.url_part not in d:
            return (0, 0, 0)

        return d[info.url_part].firmware_version_latest

    def reset_latest_fws(self):
        self.update_latest_fws(LatestFirmwares({}, {}, {}, {}, {}, {}))

    def update_latest_fws(self, latest_fws):
        self._latest_fws = latest_fws

        for info in self._infos.values():
            info.update_firmware_version_latest()

        self.sync()

    def get_latest_fws(self):
        return self._latest_fws

inventory = Inventory()
