# -*- coding: utf-8 -*-
"""
Dust Detector Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

dust_detector.py: Dust Detector Plugin Implementation

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
from brickv.bindings.bricklet_dust_detector import BrickletDustDetector
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class DustDetector(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletDustDetector, *args)

        self.dust_detector = self.device

        self.cbe_dust_density = CallbackEmulator(self.dust_detector.get_dust_density,
                                                 self.cb_dust_density,
                                                 self.increase_error_count)

        self.current_dust_density = CurveValueWrapper()

        plots = [('Dust Density', Qt.red, self.current_dust_density, '{} µg/m³'.format)]
        self.plot_widget = PlotWidget('Dust Density [µg/m³]', plots, y_resolution=1.0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def cb_dust_density(self, dust_density):
        self.current_dust_density.value = dust_density

    def start(self):
        self.cbe_dust_density.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_dust_density.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDustDetector.DEVICE_IDENTIFIER
