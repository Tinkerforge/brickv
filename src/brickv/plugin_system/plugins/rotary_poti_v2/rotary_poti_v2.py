# -*- coding: utf-8 -*-
"""
Rotary Poti 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

rotary_poti_v2.py: Rotary Poti 2.0 Plugin implementation

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
from PyQt5.QtWidgets import QHBoxLayout

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_rotary_poti_v2 import BrickletRotaryPotiV2
from brickv.plot_widget import PlotWidget
from brickv.knob_widget import KnobWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class RotaryPotiV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletRotaryPotiV2, *args)

        self.rp = self.device

        self.cbe_position = CallbackEmulator(self.rp.get_position,
                                             self.cb_position,
                                             self.increase_error_count)

        self.position_knob = KnobWidget(self)
        self.position_knob.setFocusPolicy(Qt.NoFocus)
        self.position_knob.set_total_angle(300)
        self.position_knob.set_range(-150, 150)
        self.position_knob.set_scale(30, 3)
        self.position_knob.set_knob_radius(25)

        self.current_position = None

        plots = [('Position', Qt.red, lambda: self.current_position, str)]
        self.plot_widget = PlotWidget('Position', plots, curve_motion_granularity=40, update_interval=0.025)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.position_knob)

    def start(self):
        async_call(self.rp.get_position, None, self.cb_position, self.increase_error_count)
        self.cbe_position.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_position.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryPotiV2.DEVICE_IDENTIFIER

    def cb_position(self, position):
        self.current_position = position
        self.position_knob.set_value(position)
