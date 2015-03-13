# -*- coding: utf-8 -*-  
"""
Tilt Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

tilt.py: Tilt Plugin Implementation

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
from brickv.bindings.bricklet_tilt import BrickletTilt
from brickv.utils import CallbackEmulator

from brickv.bmp_to_pixmap import bmp_to_pixmap

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout

class Tilt(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletTilt, *args)

        self.tilt = self.device

        self.cbe_tilt_state = CallbackEmulator(self.tilt.get_tilt_state,
                                               self.cb_tilt_state,
                                               self.increase_error_count)

        self.label = QLabel("Closed")
        self.closed_pixmap = bmp_to_pixmap('plugin_system/plugins/tilt/tilt_closed.bmp')
        self.open_pixmap = bmp_to_pixmap('plugin_system/plugins/tilt/tilt_open.bmp')
        self.closed_vibrationg_pixmap = bmp_to_pixmap('plugin_system/plugins/tilt/tilt_closed_vibrating.bmp')
        
        self.image_label = QLabel("")
        self.image_label.setPixmap(self.closed_pixmap)
        
        layout = QVBoxLayout(self)
        layout.addStretch()
        
        h_layout1 = QHBoxLayout()
        h_layout1.addStretch()
        h_layout1.addWidget(self.label)
        h_layout1.addStretch()
        
        h_layout2 = QHBoxLayout()
        h_layout2.addStretch()
        h_layout2.addWidget(self.image_label)
        h_layout2.addStretch()
        
        layout.addLayout(h_layout1)
        layout.addLayout(h_layout2)
        layout.addStretch()
        
    def cb_tilt_state(self, state):
        if state == 0:
            self.label.setText("Closed")
            self.image_label.setPixmap(self.closed_pixmap)
        elif state == 1:
            self.label.setText("Open")
            self.image_label.setPixmap(self.open_pixmap)
        elif state == 2:
            self.label.setText("Closed Vibrating")
            self.image_label.setPixmap(self.closed_vibrationg_pixmap)

    def start(self):
        self.cbe_tilt_state.set_period(25)
        
    def stop(self):
        self.cbe_tilt_state.set_period(0)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'tilt'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTilt.DEVICE_IDENTIFIER
