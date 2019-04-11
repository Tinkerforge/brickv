# -*- coding: utf-8 -*-
"""
Temperature 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

temperature_v2.py: Temperature 2.0 Plugin Implementation

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
from brickv.bindings.bricklet_temperature_v2 import BrickletTemperatureV2
from brickv.async_call import async_call
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class TemperatureV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletTemperatureV2, *args)

        self.tem = self.device

        self.cbe_temperature = CallbackEmulator(self.tem.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_temperature = CurveValueWrapper() # float, °C

        plots_temperature = [('Temperature', Qt.red, self.current_temperature, '{} °C'.format)]
        self.plot_widget_temperature = PlotWidget('Temperature [°C]', plots_temperature, y_resolution=0.01)

        self.enable_heater = QCheckBox("Enable Heater")
        self.enable_heater.stateChanged.connect(self.enable_heater_changed)

        layout_plot = QHBoxLayout()
        layout_plot.addWidget(self.plot_widget_temperature)

        layout_config = QHBoxLayout()
        layout_config.addStretch()
        layout_config.addWidget(self.enable_heater)
        layout_config.addStretch()

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot)
        layout_main.addLayout(layout_config)

    def enable_heater_changed(self, state):
        if state == Qt.Checked:
            self.tem.set_heater_configuration(self.tem.HEATER_CONFIG_ENABLED)
        else:
            self.tem.set_heater_configuration(self.tem.HEATER_CONFIG_DISABLED)

    def start(self):
        async_call(self.tem.get_heater_configuration, None, self.get_heater_configuration_async, self.increase_error_count)

        self.cbe_temperature.set_period(250)

        self.plot_widget_temperature.stop = False

    def stop(self):
        self.cbe_temperature.set_period(0)

        self.plot_widget_temperature.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTemperatureV2.DEVICE_IDENTIFIER

    def cb_temperature(self, temperature):
        self.current_temperature.value = temperature / 100.0

    def get_heater_configuration_async(self, heater_config):
        if heater_config == 0:
            self.enable_heater.setChecked(False)
        else:
            self.enable_heater.setChecked(True)
