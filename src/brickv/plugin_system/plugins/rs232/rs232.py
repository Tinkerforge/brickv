# -*- coding: utf-8 -*-  
"""
RS232 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

rs232.py: RS232 Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_rs232 import BrickletRS232
from brickv.async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class RS232(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRS232, *args)
        
        self.rs232 = self.device
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(QLabel('TODO'))
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)

    def start(self):
        pass
        
    def stop(self):
        pass

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rs232'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS232.DEVICE_IDENTIFIER
