# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2009 Olaf Lüke <olaf@tinkerforge.com>

plugin_manager.py: Plugins register themselves here

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

import os
from program_path import ProgramPath
from plugin_system.unknown import Unknown

class PluginManager:
    def __init__(self):
        self.plugins = []
        
        d = os.path.join(ProgramPath.program_path(), 'plugin_system/plugins/')

        for p in os.listdir(d):
            if os.path.isdir(os.path.join(d, p)):
                try:
                    m = __import__('plugins', globals(), locals(), [p], -1)
                except ImportError:
                    print('Exception in plugin: ' + str(p))
                    continue
                    
                module = getattr(m, p)
                
                try:
                    device_class = module.device_class
                except AttributeError:
                    print('Exception in plugin: ' + str(p))
                    device_class = None

                print('Found plugin: ' + str(p))
                if device_class:
                    self.plugins.append(device_class)

    def get_plugin(self, device_identifier, ipcon, uid, version):
        for plugin in self.plugins:
            if plugin.has_device_identifier(device_identifier):
                return plugin(ipcon, uid, version)

        return Unknown(ipcon, uid, version)
