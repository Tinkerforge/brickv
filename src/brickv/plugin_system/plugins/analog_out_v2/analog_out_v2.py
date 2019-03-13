# -*- coding: utf-8 -*-
"""
Analog Out 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

analog_out_v2.py: Analog Out 2.0 Plugin Implementation

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

from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_analog_out_v2 import BrickletAnalogOutV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class VoltageLabel(QLabel):
    def setText(self, voltage):
        text = "Input Voltage: {:.2f} V".format(round(voltage / 1000.0, 2))
        super().setText(text)

class AnalogOutV2(PluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletAnalogOutV2, *args)

        self.ao = self.device

        self.input_voltage_label = VoltageLabel()

        self.output_voltage_label = QLabel('Output Voltage [mV]:')
        self.output_voltage_box = QSpinBox()
        self.output_voltage_box.setMinimum(0)
        self.output_voltage_box.setMaximum(12000)
        self.output_voltage_box.setSingleStep(1)

        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.output_voltage_label)
        layout_h1.addWidget(self.output_voltage_box)
        layout_h1.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.input_voltage_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addLayout(layout_h1)
        layout.addStretch()

        self.output_voltage_box.editingFinished.connect(self.voltage_finished)

        self.cbe_input_voltage = CallbackEmulator(self.ao.get_input_voltage,
                                                  self.cb_get_input_voltage,
                                                  self.increase_error_count)

    def start(self):
        async_call(self.ao.get_output_voltage, None, self.cb_get_output_voltage, self.increase_error_count)
        async_call(self.ao.get_input_voltage, None, self.cb_get_input_voltage, self.increase_error_count)
        self.cbe_input_voltage.set_period(1000)

    def stop(self):
        self.cbe_input_voltage.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogOutV2.DEVICE_IDENTIFIER

    def cb_get_output_voltage(self, voltage):
        self.output_voltage_box.setValue(voltage)

    def cb_get_input_voltage(self, voltage):
        self.input_voltage_label.setText(voltage)

    def voltage_finished(self):
        value = self.output_voltage_box.value()
        try:
            self.ao.set_output_voltage(value)
        except ip_connection.Error:
            return
