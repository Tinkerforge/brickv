# -*- coding: utf-8 -*-
"""
Humidity 2.0 Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

humidity_v2.py: Humidity 2.0 Plugin Implementation

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
from brickv.bindings.bricklet_humidity_v2 import BrickletHumidityV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper, MovingAverageConfig
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class HumidityV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletHumidityV2, *args)

        self.hum = self.device

        self.cbe_humidity = CallbackEmulator(self.hum.get_humidity,
                                             self.cb_humidity,
                                             self.increase_error_count)

        self.cbe_temperature = CallbackEmulator(self.hum.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_humidity = CurveValueWrapper() # float, %RH
        self.current_temperature = CurveValueWrapper() # float, °C

        moving_average_humidity = MovingAverageConfig(1, 1000, self.new_moving_average_humidity)
        plots_humidity = [('Relative Humidity', Qt.red, self.current_humidity, '{} %RH'.format)]
        self.plot_widget_humidity = PlotWidget('Relative Humidity [%RH]', plots_humidity,
                                               moving_average_config=moving_average_humidity, y_resolution=0.01)

        moving_average_temperature = MovingAverageConfig(1, 1000, self.new_moving_average_temperature)
        plots_temperature = [('Temperature', Qt.red, self.current_temperature, '{} °C'.format)]
        self.plot_widget_temperature = PlotWidget('Temperature [°C]', plots_temperature,
                                                  moving_average_config=moving_average_temperature, y_resolution=0.01)

        self.enable_heater = QCheckBox("Enable Heater")
        self.enable_heater.stateChanged.connect(self.enable_heater_changed)

        layout_plot = QHBoxLayout()
        layout_plot.addWidget(self.plot_widget_humidity)
        layout_plot.addWidget(self.plot_widget_temperature)

        layout_config = QHBoxLayout()
        layout_config.addStretch()
        layout_config.addWidget(self.enable_heater)
        layout_config.addStretch()

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot)
        layout_main.addLayout(layout_config)

    def new_moving_average_humidity(self, value):
        self.hum.set_moving_average_configuration(value, self.plot_widget_temperature.get_moving_average_value())

    def new_moving_average_temperature(self, value):
        self.hum.set_moving_average_configuration(self.plot_widget_humidity.get_moving_average_value(), value)

    def enable_heater_changed(self, state):
        if state == Qt.Checked:
            self.hum.set_heater_configuration(self.hum.HEATER_CONFIG_ENABLED)
        else:
            self.hum.set_heater_configuration(self.hum.HEATER_CONFIG_DISABLED)

    def start(self):
        async_call(self.hum.get_humidity, None, self.cb_humidity, self.increase_error_count)
        async_call(self.hum.get_temperature, None, self.cb_temperature, self.increase_error_count)
        async_call(self.hum.get_heater_configuration, None, self.cb_heater_configuration, self.increase_error_count)
        async_call(self.hum.get_moving_average_configuration, None, self.cb_moving_average_configuration, self.increase_error_count)

        self.cbe_humidity.set_period(100)
        self.cbe_temperature.set_period(100)

        self.plot_widget_humidity.stop = False
        self.plot_widget_temperature.stop = False

    def stop(self):
        self.cbe_humidity.set_period(0)
        self.cbe_temperature.set_period(0)

        self.plot_widget_humidity.stop = True
        self.plot_widget_temperature.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHumidityV2.DEVICE_IDENTIFIER

    def cb_humidity(self, humidity):
        self.current_humidity.value = humidity / 100.0

    def cb_temperature(self, temperature):
        self.current_temperature.value = temperature / 100.0

    def cb_heater_configuration(self, heater_config):
        if heater_config == 0:
            self.enable_heater.setChecked(False)
        else:
            self.enable_heater.setChecked(True)

    def cb_moving_average_configuration(self, average):
        self.plot_widget_humidity.set_moving_average_value(average.moving_average_length_humidity)
        self.plot_widget_temperature.set_moving_average_value(average.moving_average_length_temperature)
