# -*- coding: utf-8 -*-
"""
Linear Poti 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

linear_poti_v2.py: Linear Poti 2.0 Plugin implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QSlider

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_linear_poti_v2 import BrickletLinearPotiV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.callback_emulator import CallbackEmulator

class LinearPotiV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletLinearPotiV2, *args)

        self.lp = self.device

        self.cbe_position = CallbackEmulator(self.lp.get_position,
                                             self.cb_position,
                                             self.increase_error_count)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setMinimumWidth(200)

        self.current_position = CurveValueWrapper()

        plots = [('Position', Qt.red, self.current_position, str)]
        self.plot_widget = PlotWidget('Position', plots, extra_key_widgets=[self.slider],
                                      update_interval=0.025, y_resolution=1.0)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        self.cbe_position.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_position.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLinearPotiV2.DEVICE_IDENTIFIER

    def cb_position(self, position):
        self.current_position.value = position
        self.slider.setValue(position)
