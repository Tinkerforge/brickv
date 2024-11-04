# -*- coding: utf-8 -*-
"""
Multi IO Plugin
Copyright (C) 2024 Matthias Bolte <matthias@tinkerforge.com>

multi_io.py: Multi IO Plugin Implementation

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
from brickv.plugin_system.plugins.multi_io.ui_multi_io import Ui_MultiIO
from brickv.bindings.bricklet_multi_io import BrickletMultiIO
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MultiIO(COMCUPluginBase, Ui_MultiIO):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletMultiIO, *args)

        self.setupUi(self)

        self.cbe_inputs = CallbackEmulator(self,
                                           self.device.get_inputs,
                                           None,
                                           self.cb_inputs,
                                           self.increase_error_count)

        self.label_input_values = [self.label_input_0_value,
                                   self.label_input_1_value,
                                   self.label_input_2_value,
                                   self.label_input_3_value,
                                   self.label_input_4_value,
                                   self.label_input_5_value,
                                   self.label_input_6_value,
                                   self.label_input_7_value,
                                   self.label_input_8_value,
                                   self.label_input_9_value,
                                   self.label_input_10_value,
                                   self.label_input_11_value,
                                   self.label_input_12_value,
                                   self.label_input_13_value,
                                   self.label_input_14_value,
                                   self.label_input_15_value]

        self.combo_output_0_value.currentIndexChanged.connect(self.output_changed)
        self.combo_output_1_value.currentIndexChanged.connect(self.output_changed)

    def get_outputs_async(self, value):
        self.combo_output_0_value.setCurrentIndex(int(value[0]))
        self.combo_output_1_value.setCurrentIndex(int(value[1]))

    def start(self):
        async_call(self.device.get_outputs, None, self.get_outputs_async, self.increase_error_count)
        self.cbe_inputs.set_period(50)

    def stop(self):
        self.cbe_inputs.set_period(0)

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMultiIO.DEVICE_IDENTIFIER

    def cb_inputs(self, value):
        for channel in range(16):
            if value[channel] == BrickletMultiIO.INPUT_LOW:
                self.label_input_values[channel].setText('Low')
            elif value[channel] == BrickletMultiIO.INPUT_HIGH:
                self.label_input_values[channel].setText('High')
            elif value[channel] == BrickletMultiIO.INPUT_FLOATING:
                self.label_input_values[channel].setText('Floating')
            else: # INPUT_ERROR
                self.label_input_values[channel].setText('Error')

    def output_changed(self):
        self.device.set_outputs([
            bool(self.combo_output_0_value.currentIndex()),
            bool(self.combo_output_1_value.currentIndex()),
        ])
