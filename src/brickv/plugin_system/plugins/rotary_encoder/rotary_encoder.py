# -*- coding: utf-8 -*-  
"""
Rotary Encoder Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

rotary_encoder.py: Rotary Encoder Plugin Implementation

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
from bindings.bricklet_rotary_encoder import BrickletRotaryEncoder
from async_call import async_call

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt4.QtCore import pyqtSignal, Qt
    
class CountLabel(QLabel):
    def setText(self, text):
        text = "Count: " + text
        super(CountLabel, self).setText(text)
    
class RotaryEncoder(PluginBase):
    qtcb_count = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Rotary Encoder Bricklet', version)

        self.re = BrickletRotaryEncoder(uid, ipcon)
        
        self.qtcb_count.connect(self.cb_count)
        self.re.register_callback(self.re.CALLBACK_COUNT,
                                  self.qtcb_count.emit) 
        
        self.count_label = CountLabel('Count: 0')
        self.reset_button = QPushButton('Reset Count')
        self.reset_button.pressed.connect(self.reset_pressed)
        
        
        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(self.count_label)
        layout_h1.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.reset_button)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addLayout(layout_h2)
        layout.addStretch()
        
    def cb_count(self, count):
        self.count_label.setText(str(count))
        
    def reset_pressed(self):
        async_call(self.re.get_count, True, None, self.increase_error_count)
        self.count_label.setText(str(0))

    def start(self):
        async_call(self.re.set_count_callback_period, 100, None, self.increase_error_count)
        
    def stop(self):
        async_call(self.re.set_count_callback_period, 0, None, self.increase_error_count)

    def get_url_part(self):
        return 'rotary_encoder'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryEncoder.DEVICE_IDENTIFIER