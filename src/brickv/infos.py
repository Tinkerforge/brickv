# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012-2015 Olaf Lüke <olaf@tinkerforge.com>
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

from PyQt4.QtGui import QApplication

from brickv import config

UID_BRICKV = '$BRICKV'
UID_BRICKD = '$BRICKD'

class AbstractInfo(object):
    type = 'abstract'
    url_part = ''
    error = ''
    name = ''
    firmware_version_installed = (0, 0, 0)
    firmware_version_latest = (0, 0, 0)

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

    def __repr__(self):
        return """{0} ({1}):
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

    def get_combo_item(self):
        version_str = get_version_string(self.firmware_version_installed)

        return '{0} [{1}] ({2})'.format(self.name, self.uid, version_str)

class BrickletInfo(DeviceInfo):
    type = 'bricklet'

class BrickInfo(DeviceInfo):
    can_have_extension = False
    type = 'brick'

    def __init__(self):
        DeviceInfo.__init__(self)

        self.bricklets = {'a': None, 'b': None, 'z-a': None, 'z-b': None}

    def __repr__(self):
        a = 'Not connected'
        b = 'Not connected'
        ia = 'Not connected'
        ib = 'Not connected'
        if self.bricklets['a'] != None:
            a = '{0} ({1})'.format(self.bricklets['a'].name, self.bricklets['a'].uid)
        if self.bricklets['b'] != None:
            b = '{0} ({1})'.format(self.bricklets['b'].name, self.bricklets['b'].uid)
        if self.bricklets['z-a'] != None:
            ia = '{0} ({1})'.format(self.bricklets['z-a'].name, self.bricklets['z-a'].uid)
        if self.bricklets['z-b'] != None:
            ib = '{0} ({1})'.format(self.bricklets['z-b'].name, self.bricklets['z-b'].uid)

        return super(BrickInfo, self).__repr__() + """  Bricklets:
   a: {0}
   b: {1}
   z-a: {2}
   z-b: {3}
""".format(a, b, ia, ib)

class BrickMasterInfo(BrickInfo):
    can_have_extension = True
    connection_type = None

    def __init__(self):
        BrickInfo.__init__(self)

        self.bricklets = {'a': None, 'b': None, 'c': None, 'd': None, 'z-a': None, 'z-b': None, 'z-c': None, 'z-d': None}
        self.extensions = {'ext0': None, 'ext1': None}

    def __repr__(self):
        ext0 = 'No Extension'
        ext1 = 'No Extension'
        c = 'Not connected'
        d = 'Not connected'
        ic = 'Not connected'
        id = 'Not connected'
        if self.extensions['ext0'] != None:
            ext0 = self.extensions['ext0'].name
        if self.extensions['ext1'] != None:
            ext1 = self.extensions['ext1'].name
        if self.bricklets['c'] != None:
            c = '{0} ({1})'.format(self.bricklets['c'].name, self.bricklets['c'].uid)
        if self.bricklets['d'] != None:
            d = '{0} ({1})'.format(self.bricklets['d'].name, self.bricklets['d'].uid)
        if self.bricklets['z-c'] != None:
            ic = '{0} ({1})'.format(self.bricklets['z-c'].name, self.bricklets['z-c'].uid)
        if self.bricklets['z-d'] != None:
            id = '{0} ({1})'.format(self.bricklets['z-d'].name, self.bricklets['z-d'].uid)

        # Bricklet a and b are already printed by BrickInfo
        return BrickInfo.__repr__(self) + """   c: {0}
   d: {1}
   z-c: {2}
   z-d: {3}
  Extensions:
   ext0: {4}
   ext1: {5}
""".format(c, d, ic, id, ext0, ext1)

class BrickREDInfo(BrickInfo):
    def __init__(self):
        BrickInfo.__init__(self)

        self.bricklets = {}

def get_version_string(version_tuple):
    return '.'.join(map(str, version_tuple))

if not '_infos' in globals():
    _infos = {UID_BRICKV: ToolInfo(), UID_BRICKD: ToolInfo()}
    _infos[UID_BRICKV].name = 'Brick Viewer'
    _infos[UID_BRICKV].firmware_version_installed = tuple(map(int, config.BRICKV_VERSION.split('.')))
    _infos[UID_BRICKD].name = 'Brick Daemon'

def add_info(info):
    _infos[info.uid] = info
    get_infos_changed_signal().emit(info.uid)

def remove_info(uid):
    _infos.pop(uid)
    get_infos_changed_signal().emit(uid)

def update_info(uid):
    get_infos_changed_signal().emit(uid)

def get_info(uid):
    try:
        return _infos[uid]
    except KeyError:
        return None

def get_infos():
    return sorted(_infos.values(), key=lambda x: x.name)

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
            extension_infos += filter(lambda value: value != None, brick_info.extensions.values())

    return sorted(extension_infos, key=lambda x: x.name)

def get_infos_changed_signal():
    return QApplication.instance().infos_changed_signal
