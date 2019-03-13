# -*- coding: utf-8 -*-
"""
Air Quality Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

air_quality.py: Air Quality Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox, QLabel

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_air_quality import BrickletAirQuality
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class AirQuality(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAirQuality, *args)

        self.air_quality = self.device

        self.cbe_air_quality = CallbackEmulator(self.air_quality.get_all_values,
                                                self.cb_get_all_values,
                                                self.increase_error_count)

        self.current_iaq_index = None # float
        self.current_temperature = None # float, °C
        self.current_humidity = None # float, %RH
        self.current_air_pressure = None # float, mbar
        self.current_iaq_index_accuracy = None

        self.iaq_accuracy_label = QLabel("(Accuracy: TBD)")

        plots_iaq_index = [('IAQ Index', Qt.red, lambda: self.current_iaq_index, '{}'.format)]
        self.plot_widget_iaq_index = PlotWidget('IAQ Index', plots_iaq_index, extra_key_widgets=(self.iaq_accuracy_label, ))

        plots_temperature = [('Temperature', Qt.red, lambda: self.current_temperature, '{} °C'.format)]
        self.plot_widget_temperature = PlotWidget('Temperature [°C]', plots_temperature)

        plots_humidity = [('Relative Humidity', Qt.red, lambda: self.current_humidity, '{} %RH'.format)]
        self.plot_widget_humidity = PlotWidget('Relative Humidity [%RH]', plots_humidity)

        plots_air_pressure = [('Air Pressure', Qt.red, lambda: self.current_air_pressure, '{} mbar (QFE)'.format)]
        self.plot_widget_air_pressure = PlotWidget('Air Pressure [mbar]', plots_air_pressure)

        layout_plot1 = QHBoxLayout()
        layout_plot1.addWidget(self.plot_widget_iaq_index)
        layout_plot1.addWidget(self.plot_widget_temperature)

        layout_plot2 = QHBoxLayout()
        layout_plot2.addWidget(self.plot_widget_humidity)
        layout_plot2.addWidget(self.plot_widget_air_pressure)

        layout_main = QVBoxLayout(self)
        layout_main.addLayout(layout_plot1)
        layout_main.addLayout(layout_plot2)

    def cb_get_all_values(self, values):
        self.current_iaq_index = values.iaq_index
        self.current_iaq_index_accuracy = values.iaq_index_accuracy
        self.current_temperature = values.temperature / 100.0
        self.current_humidity = values.humidity / 100.0
        self.current_air_pressure = values.air_pressure / 100.0

        if self.current_iaq_index_accuracy == 0:
            self.iaq_accuracy_label.setText('(Accuracy: Unreliable)')
        elif self.current_iaq_index_accuracy == 1:
            self.iaq_accuracy_label.setText('(Accuracy: Low)')
        elif self.current_iaq_index_accuracy == 2:
            self.iaq_accuracy_label.setText('(Accuracy: Medium)')
        else:
            self.iaq_accuracy_label.setText('(Accuracy: High)')

    def start(self):
        async_call(self.air_quality.get_all_values, None, self.cb_get_all_values, self.increase_error_count)

        self.cbe_air_quality.set_period(500)

        self.plot_widget_iaq_index.stop = False
        self.plot_widget_temperature.stop = False
        self.plot_widget_humidity.stop = False
        self.plot_widget_air_pressure.stop = False

    def stop(self):
        self.cbe_air_quality.set_period(0)

        self.plot_widget_iaq_index.stop = True
        self.plot_widget_temperature.stop = True
        self.plot_widget_humidity.stop = True
        self.plot_widget_air_pressure.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAirQuality.DEVICE_IDENTIFIER
