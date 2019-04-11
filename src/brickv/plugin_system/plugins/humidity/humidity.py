# -*- coding: utf-8 -*-
"""
Humidity Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

humidity.py: Humidity Plugin Implementation

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
from brickv.bindings.bricklet_humidity import BrickletHumidity
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class Humidity(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletHumidity, *args)

        self.hum = self.device

        self.cbe_humidity = CallbackEmulator(self.hum.get_humidity,
                                             self.cb_humidity,
                                             self.increase_error_count)

        self.current_humidity = CurveValueWrapper() # float, %RH

        plots = [('Relative Humidity', Qt.red, self.current_humidity, '{} %RH'.format)]
        self.plot_widget = PlotWidget('Relative Humidity [%RH]', plots, y_resolution=0.1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        self.cbe_humidity.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_humidity.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHumidity.DEVICE_IDENTIFIER

    def cb_humidity(self, humidity):
        self.current_humidity.value = humidity / 10.0
