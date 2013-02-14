# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

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

import config

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

class ToolInfo(AbstractInfo):
    type = 'tool'
    
    def __repr__(self):
        return """{0}:
  version installed: {1}, 
  version latest: {2}, 
  url_part: {3}
""".format(self.name, self.firmware_version_installed,
           self.firmware_version_latest, self.url_part)

class DeviceInfo(AbstractInfo):
    uid = ''
    connected_uid = ''
    position = ''
    hardware_version = (0, 0, 0)
    device_identifier = 0
    plugin = None
    plugin_container = None
    protocol_version = 0
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
  protocol version: {8}, 
  url_part: {9}, 
  plugin: {10}, 
  plugin_container: {11}
""".format(self.name, self.uid, self.connected_uid, self.position,
           self.firmware_version_installed, self.firmware_version_latest,
           self.hardware_version, self.device_identifier,
           self.protocol_version, self.url_part,
           self.plugin, self.plugin_container)

    def get_combo_item(self):
        version_str = get_version_string(self.firmware_version_installed)

        if type == 'brick':
            return '{0} [{1}] ({2})'.format(self.name, self.uid, version_str)
        else:
            if self.protocol_version < 2:
                return '{0} ({1})'.format(self.name, version_str)
            else:
                return '{0} [{1}] ({2})'.format(self.name, self.uid, version_str)

class BrickletInfo(DeviceInfo):
    type = 'bricklet'
    
class BrickInfo(DeviceInfo):
    type = 'brick'
    
    def __init__(self):
        self.bricklets = {'a': None, 'b': None}
    
    def __repr__(self):
        a = 'Not connected'
        b = 'Not connected'
        if self.bricklets['a'] != None:
            a = '{0} ({1})'.format(self.bricklets['a'].name, self.bricklets['a'].uid)
        if self.bricklets['b'] != None:
            b = '{0} ({1})'.format(self.bricklets['b'].name, self.bricklets['b'].uid)
            
        return super(BrickInfo, self).__repr__() + """  Bricklets:
   a: {0}
   b: {1}
""".format(a, b)
    
class BrickMasterInfo(BrickInfo):
    def __init__(self):
        self.bricklets = {'a': None, 'b': None, 'c': None, 'd': None}
    
    def __repr__(self):
        a = 'Not connected'
        b = 'Not connected'
        c = 'Not connected'
        d = 'Not connected'
        if self.bricklets['a'] != None:
            a = '{0} ({1})'.format(self.bricklets['a'].name, self.bricklets['a'].uid)
        if self.bricklets['b'] != None:
            b = '{0} ({1})'.format(self.bricklets['b'].name, self.bricklets['b'].uid)
        if self.bricklets['c'] != None:
            c = '{0} ({1})'.format(self.bricklets['c'].name, self.bricklets['c'].uid)
        if self.bricklets['d'] != None:
            d = '{0} ({1})'.format(self.bricklets['d'].name, self.bricklets['d'].uid)
            
        return super(BrickInfo, self).__repr__() + """  Bricklets:
   a: {0}
   b: {1}
   c: {2}
   d: {3} 
""".format(a, b, c, d)

def get_version_string(version_tuple):
    return '.'.join(map(str, version_tuple))

if not 'infos' in globals():
    infos = {UID_BRICKV: ToolInfo(), UID_BRICKD: ToolInfo()}
    infos[UID_BRICKV].name = 'Brick Viewer'
    infos[UID_BRICKV].firmware_version_installed = tuple(map(int, config.BRICKV_VERSION.split('.')))
    infos[UID_BRICKD].name = 'Brick Daemon'
