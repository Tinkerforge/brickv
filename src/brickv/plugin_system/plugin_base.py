# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer)
Copyright (C) 2009-2012 Olaf Lüke <olaf@tinkerforge.com>

plugin_base.py: Base class for all Brick Viewer Plugins

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

from PyQt4.QtGui import QWidget

class PluginBase(QWidget, object):
    def __init__(self, ipcon, uid, name, version):
        QWidget.__init__(self)
        self.label_timeouts = None
        self.ipcon = ipcon
        self.uid = uid
        self.name = name
        self.version = version
        self.version_str = '.'.join(map(str, version))
        self.error_count = 0
        
    def increase_error_count(self):
        self.error_count += 1
        if self.label_timeouts:
            self.label_timeouts.setText('{0}'.format(self.error_count))
        
    # To be overridden by inheriting class
    def stop(self):
        pass
    
    def start(self):
        pass
    
    def destroy(self):
        pass

    def has_reset_device(self):
        return False

    def reset_device(self):
        pass

    def is_brick(self):
        return False

    def is_hardware_version_relevant(self):
        return False

    def get_url_part(self):
        return 'UNKNOWN'

    @staticmethod
    def has_device_identifier(device_identifier):
        return False
