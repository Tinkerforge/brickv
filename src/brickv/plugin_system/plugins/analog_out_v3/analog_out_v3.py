# -*- coding: utf-8 -*-
"""
Analog Out 3.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

analog_out_v3.py: Analog Out 3.0 Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_analog_out_v3 import BrickletAnalogOutV3
from brickv.plugin_system.plugins.analog_out_v3.ui_analog_out_v3 import Ui_AnalogOutV3
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class AnalogOutV3(COMCUPluginBase, Ui_AnalogOutV3):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletAnalogOutV3, *args)

        self.setupUi(self)
        self.ao = self.device

        self.output_voltage_box.editingFinished.connect(self.voltage_finished)

        self.cbe_input_voltage = CallbackEmulator(self.ao.get_input_voltage,
                                                  None,
                                                  self.cb_input_voltage,
                                                  self.increase_error_count)

    def start(self):
        async_call(self.ao.get_output_voltage, None, self.get_output_voltage_async, self.increase_error_count)

        self.cbe_input_voltage.set_period(1000)

    def stop(self):
        self.cbe_input_voltage.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogOutV3.DEVICE_IDENTIFIER

    def get_output_voltage_async(self, voltage):
        self.output_voltage_box.setValue(voltage / 1000.0)

    def cb_input_voltage(self, voltage):
        self.input_voltage_label.setText("{:.3f} V".format(round(voltage / 1000.0, 2)))

    def voltage_finished(self):
        value = int(round(self.output_voltage_box.value() * 1000, 0))

        try:
            self.ao.set_output_voltage(value)
        except ip_connection.Error:
            return
