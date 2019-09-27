# -*- coding: utf-8 -*-
"""
Gas Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

gas.py: Gas Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_gas import BrickletGas
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import get_main_window

class Gas(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletGas, *args)

        self.gas = self.device

        self.cbe_values = CallbackEmulator(self.gas.get_values,
                                           None,
                                           self.cb_values,
                                           self.increase_error_count)

        self.current_ppm = CurveValueWrapper() # PPM

        plots_ppm = [('', Qt.red, self.current_ppm, self.format_value)]
        self.plot_widget_ppm = PlotWidget('TBD [TBD]', plots_ppm, y_resolution=1)

        layout_plot = QHBoxLayout()
        layout_plot.addWidget(self.plot_widget_ppm)

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot)

        self.gas_type = 0

    def start(self):
        async_call(self.gas.get_values, None, self.get_values_async, self.increase_error_count)

        self.cbe_values.set_period(250)

        self.plot_widget_ppm.stop = False

    def stop(self):
        self.cbe_values.set_period(0)

        self.plot_widget_ppm.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletGas.DEVICE_IDENTIFIER

    def update_name(self, gas_text, y_scale_text):
        index = get_main_window().tab_widget.currentIndex()
        get_main_window().tab_widget.setTabText(index, 'Gas Bricklet ({0})'.format(gas_text))
        self.plot_widget_ppm.plot.y_scale.title_text = y_scale_text 

    def get_values_async(self, values):
        self.gas_type = values.gas_type

        if values.gas_type == BrickletGas.GAS_TYPE_CO:
            self.update_name('CO', 'PPM [CO]')
        else:
            self.update_name('?', 'PPM [?]')

        self.cb_values(values)
        print(values)

    def format_value(self, value):
        if self.gas_type == BrickletGas.GAS_TYPE_CO:
            return 'CO Concentration: ' + str(value) + ' PPM'
        else:
            return 'Unkown Concentration: ' + str(value)

    def cb_values(self, values):
        if self.gas_type == BrickletGas.GAS_TYPE_CO:
            self.current_ppm.value = int(values.gas_concentration/1000.0)
        else:
            self.current_ppm.value = int(values.gas_concentration/1000.0)