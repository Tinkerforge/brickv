# -*- coding: utf-8 -*-  
"""
Moisture Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

moisture.py: Moisture Plugin Implementation

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_moisture import BrickletMoisture
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MoistureLabel(QLabel):
    def setText(self, text):
        text = "Moisture Value: " + text
        super(MoistureLabel, self).setText(text)
    
class Moisture(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletMoisture, *args)

        self.moisture = self.device

        self.cbe_moisture = CallbackEmulator(self.moisture.get_moisture_value,
                                             self.cb_moisture,
                                             self.increase_error_count)

        self.moisture_label = MoistureLabel()
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Moisture', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.moisture_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        
    def get_current_value(self):
        return self.current_value

    def cb_moisture(self, moisture):
        self.current_value = moisture
        self.moisture_label.setText(str(moisture))

    def start(self):
        async_call(self.moisture.get_moisture_value, None, self.cb_moisture, self.increase_error_count)
        self.cbe_moisture.set_period(100)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_moisture.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'moisture'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMoisture.DEVICE_IDENTIFIER
