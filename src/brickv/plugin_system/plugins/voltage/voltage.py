# -*- coding: utf-8 -*-
"""
Voltage Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

voltage.py: Voltage Plugin Implementation

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
from brickv.bindings.bricklet_voltage import BrickletVoltage
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_voltage

class Voltage(PluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletVoltage, *args)

        self.vol = self.device

        self.cbe_voltage = CallbackEmulator(self.vol.get_voltage,
                                            self.cb_voltage,
                                            self.increase_error_count)

        self.current_voltage = None # float, V

        plots = [('Voltage', Qt.red, lambda: self.current_voltage, format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.vol.get_voltage, None, self.cb_voltage, self.increase_error_count)
        self.cbe_voltage.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_voltage.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletVoltage.DEVICE_IDENTIFIER

    def cb_voltage(self, voltage):
        self.current_voltage = voltage / 1000.0
