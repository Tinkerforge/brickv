# -*- coding: utf-8 -*-  
"""
Industrial Dual Analog In Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

industrial_dual_analog_in.py: Industrial Dual Analog In Plugin Implementation

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

import functools

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_industrial_dual_analog_in import BrickletIndustrialDualAnalogIn
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox
from PyQt4.QtCore import Qt

class VoltageLabel(QLabel):
    def setText(self, text):
        text = text + " V"
        super(VoltageLabel, self).setText(text)

class IndustrialDualAnalogIn(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIndustrialDualAnalogIn, *args)

        self.analog_in = self.device

        self.cbe_voltage0 = CallbackEmulator(functools.partial(self.analog_in.get_voltage, 0),
                                             functools.partial(self.cb_voltage, 0),
                                             self.increase_error_count)
        self.cbe_voltage1 = CallbackEmulator(functools.partial(self.analog_in.get_voltage, 1),
                                             functools.partial(self.cb_voltage, 1),
                                             self.increase_error_count)

        self.voltage_label = [VoltageLabel(), VoltageLabel()]
        
        self.sample_rate_label1 = QLabel('Sample Rate:')
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItem('976')
        self.sample_rate_combo.addItem('488')
        self.sample_rate_combo.addItem('244')
        self.sample_rate_combo.addItem('122')
        self.sample_rate_combo.addItem('61')
        self.sample_rate_combo.addItem('4')
        self.sample_rate_combo.addItem('2')
        self.sample_rate_combo.addItem('1')
        self.sample_rate_label2 = QLabel('Samples per second')
        
        self.voltage_value = [None, None]
        
        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)
        
        plot_list = [['Channel 0', Qt.red, self.get_voltage_value0],
                     ['Channel 1', Qt.blue, self.get_voltage_value1]]
        self.plot_widget = PlotWidget('Voltage [V]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(QLabel("Channel 0: "))
        layout_h.addWidget(self.voltage_label[0])
        layout_h.addStretch()

        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(QLabel("Channel 1: "))
        layout_h1.addWidget(self.voltage_label[1])
        layout_h1.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.sample_rate_label1)
        layout_h2.addWidget(self.sample_rate_combo)
        layout_h2.addWidget(self.sample_rate_label2)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h1)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_h2)
        
    def start(self):
        async_call(self.analog_in.get_voltage, 0, lambda x: self.cb_voltage(0, x), self.increase_error_count)
        async_call(self.analog_in.get_voltage, 1, lambda x: self.cb_voltage(1, x), self.increase_error_count)
        self.cbe_voltage0.set_period(100)
        self.cbe_voltage1.set_period(100)
        
        async_call(self.analog_in.get_sample_rate, None, self.get_sample_rate_async, self.increase_error_count)
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_voltage0.set_period(0)
        self.cbe_voltage1.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'industrial_dual_analog_in'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDualAnalogIn.DEVICE_IDENTIFIER

    def get_voltage_value0(self):
        return self.voltage_value[0]
    
    def get_voltage_value1(self):
        return self.voltage_value[1]
    
    def update_connected(self):
        pass
    
    def sample_rate_combo_index_changed(self, index):
        async_call(self.analog_in.set_sample_rate, index, None, self.increase_error_count)
    
    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.setCurrentIndex(rate)

    def cb_voltage(self, sensor, voltage):
        value = voltage/1000.0
        self.voltage_label[sensor].setText('%6.03f' % round(value, 3))
        self.voltage_value[sensor] = value
