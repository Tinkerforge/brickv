# -*- coding: utf-8 -*-  
"""
Analog Out Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

analog_out.py: Analog Out Plugin Implementation

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
from bindings import ip_connection
from bindings.bricklet_analog_out import BrickletAnalogOut
from async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox

class AnalogOut(PluginBase):
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Analog Out Bricklet', version)
        
        self.ao = BrickletAnalogOut(uid, ipcon)
        
        self.voltage_label = QLabel('Output Voltage (mV): ')
        self.voltage_box = QSpinBox()
        self.voltage_box.setMinimum(0)
        self.voltage_box.setMaximum(5000)
        self.voltage_box.setSingleStep(1)
        self.mode_label = QLabel('Mode: ')
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Normal Mode")
        self.mode_combo.addItem("1k Ohm resistor to ground")
        self.mode_combo.addItem("100k Ohm resistor to ground")
        self.mode_combo.addItem("500k Ohm resistor to ground")
        
        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.voltage_label)
        layout_h1.addWidget(self.voltage_box)
        layout_h1.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.mode_label)
        layout_h2.addWidget(self.mode_combo)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addLayout(layout_h1)
        layout.addStretch()
        
        self.voltage_box.editingFinished.connect(self.voltage_finished)
        self.mode_combo.activated.connect(self.mode_changed)
        
    def start(self):
        async_call(self.ao.get_voltage, None, self.voltage_box.setValue, self.increase_error_count)
        async_call(self.ao.get_mode, None, self.mode_combo.setCurrentIndex, self.increase_error_count)
        
    def stop(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogOut.DEVICE_IDENTIFIER
    
    def voltage_finished(self):
        value = self.voltage_box.value()
        try:
            self.ao.set_voltage(value)
        except ip_connection.Error:
            return
        
        self.mode_combo.setCurrentIndex(0)
        
    def mode_changed(self, mode):
        try:
            self.ao.set_mode(mode)
        except ip_connection.Error:
            return
        
        self.voltage_box.setValue(0)
