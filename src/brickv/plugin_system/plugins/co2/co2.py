# -*- coding: utf-8 -*-
"""
CO2 Bricklet Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

co2.py: CO2 Bricklet Plugin Implementation

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
from brickv.bindings.bricklet_co2 import BrickletCO2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class CO2(PluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletCO2, *args)

        self.co2 = self.device

        self.cbe_co2_concentration = CallbackEmulator(self.co2.get_co2_concentration,
                                                      self.cb_co2_concentration,
                                                      self.increase_error_count)

        self.current_co2_concentration = None # int, ppm

        plots = [('CO2 Concentration', Qt.red, lambda: self.current_co2_concentration, '{} ppm'.format)]
        self.plot_widget = PlotWidget('CO2 Concentration [ppm]', plots)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.co2.get_co2_concentration, None, self.cb_co2_concentration, self.increase_error_count)
        self.cbe_co2_concentration.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_co2_concentration.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCO2.DEVICE_IDENTIFIER

    def cb_co2_concentration(self, co2_concentration):
        self.current_co2_concentration = co2_concentration
