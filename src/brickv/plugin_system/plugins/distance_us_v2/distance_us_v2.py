# -*- coding: utf-8 -*-
"""
Distance US 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

distance_us_v2.py: Distance US 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_distance_us_v2 import BrickletDistanceUSV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

class DistanceUSV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletDistanceUSV2, *args)

        self.dist = self.device

        self.cbe_distance = CallbackEmulator(self,
                                             self.dist.get_distance,
                                             None,
                                             self.cb_distance,
                                             self.increase_error_count)

        self.current_distance = CurveValueWrapper()

        plots = [('Distance', Qt.red, self.current_distance, '{:.1f} cm'.format)]
        self.plot_widget = PlotWidget('Distance [cm]', plots, y_resolution=1.0)


        self.update_rate_label = QLabel('Update Rate:')
        self.update_rate_combo = QComboBox()
        self.update_rate_combo.addItem(" 2 Hz")
        self.update_rate_combo.addItem("10 Hz")

        self.update_rate_combo.currentIndexChanged.connect(self.new_update_rate)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.update_rate_label)
        hlayout.addWidget(self.update_rate_combo)
        hlayout.addStretch()

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addLayout(hlayout)

    def new_update_rate(self):
        update_rate = self.update_rate_combo.currentIndex()
        self.dist.set_update_rate(update_rate)

    def get_update_rate_async(self, update_rate):
        self.update_rate_combo.setCurrentIndex(update_rate)

    def start(self):
        async_call(self.dist.get_update_rate, None, self.get_update_rate_async, self.increase_error_count)
        self.cbe_distance.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_distance.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDistanceUSV2.DEVICE_IDENTIFIER

    def cb_distance(self, distance):
        self.current_distance.value = distance / 10.0
