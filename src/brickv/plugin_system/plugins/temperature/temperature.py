# -*- coding: utf-8 -*-
"""
Temperature Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

temperature.py: Temperature Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_temperature import BrickletTemperature
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class Temperature(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletTemperature, *args)

        self.tem = self.device

        self.cbe_temperature = CallbackEmulator(self.tem.get_temperature,
                                                None,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_temperature = CurveValueWrapper() # float, °C

        plots = [('Temperature', Qt.red, self.current_temperature, '{:.2f} °C'.format)]
        self.plot_widget = PlotWidget('Temperature [°C]', plots, y_resolution=0.01)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        self.cbe_temperature.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_temperature.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTemperature.DEVICE_IDENTIFIER

    def cb_temperature(self, temperature):
        self.current_temperature.value = temperature / 100.0
