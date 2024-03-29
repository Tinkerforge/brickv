# -*- coding: utf-8 -*-
"""
CO2 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

co2_v2.py: CO2 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_co2_v2 import BrickletCO2V2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class CO2V2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletCO2V2, *args)

        self.co2 = self.device

        self.cbe_all_values = CallbackEmulator(self,
                                               self.co2.get_all_values,
                                               None,
                                               self.cb_all_values,
                                               self.increase_error_count)

        self.current_co2 = CurveValueWrapper() # int, ppm
        self.current_temperature = CurveValueWrapper() # float, °C
        self.current_humidity = CurveValueWrapper() # float, %RH

        plots_co2 = [('CO2', Qt.red, self.current_co2, '{} PPM'.format)]
        self.plot_widget_co2 = PlotWidget('CO2 [PPM]', plots_co2, y_resolution=1.0)

        plots_temperature = [('Temperature', Qt.red, self.current_temperature, '{} °C'.format)]
        self.plot_widget_temperature = PlotWidget('Temperature [°C]', plots_temperature, y_resolution=0.01)

        plots_humidity = [('Relative Humidity', Qt.red, self.current_humidity, '{} %RH'.format)]
        self.plot_widget_humidity = PlotWidget('Relative Humidity [%RH]', plots_humidity, y_resolution=0.01)

        layout_plot1 = QHBoxLayout()
        layout_plot1.addWidget(self.plot_widget_co2)

        layout_plot2 = QHBoxLayout()
        layout_plot2.addWidget(self.plot_widget_temperature)
        layout_plot2.addWidget(self.plot_widget_humidity)

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot1)
        layout_main.addLayout(layout_plot2)

    def cb_all_values(self, values):
        self.current_co2.value = values.co2_concentration
        self.current_temperature.value = values.temperature / 100.0
        self.current_humidity.value = values.humidity / 100.0

    def start(self):
        self.cbe_all_values.set_period(250)

        self.plot_widget_co2.stop = False
        self.plot_widget_temperature.stop = False
        self.plot_widget_humidity.stop = False

    def stop(self):
        self.cbe_all_values.set_period(0)

        self.plot_widget_co2.stop = True
        self.plot_widget_temperature.stop = True
        self.plot_widget_humidity.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCO2V2.DEVICE_IDENTIFIER
