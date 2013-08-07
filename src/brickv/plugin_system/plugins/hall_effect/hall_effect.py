# -*- coding: utf-8 -*-  
"""
Hall Effect Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

hall_effect.py: Hall Effect Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from bindings.bricklet_hall_effect import BrickletHallEffect
from async_call import async_call

from PyQt4.QtGui import QLabel, QVBoxLayout
    
class HallEffect(PluginBase):
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Hall Effect Bricklet', version)

        self.hf = BrickletHallEffect(uid, ipcon)
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addWidget(QLabel("The Bricklet is not yet supported in this version of Brickv. Please update Brickv."))
        layout.addStretch()
        

    def start(self):
        pass
        
    def stop(self):
        pass

    def get_url_part(self):
        return 'hall_effect'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHallEffect.DEVICE_IDENTIFIER