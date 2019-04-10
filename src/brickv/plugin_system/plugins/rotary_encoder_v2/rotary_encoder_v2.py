# -*- coding: utf-8 -*-
"""
Rotary Encoder V2 Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

rotary_encoder_v2.py: Rotary Encoder V2 Plugin Implementation

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

import functools

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_rotary_encoder_v2 import BrickletRotaryEncoderV2
from brickv.knob_widget import KnobWidget
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class RotaryEncoderV2(COMCUPluginBase):
    qtcb_pressed = pyqtSignal()
    qtcb_released = pyqtSignal()

    def __init__(self, *args):
        super().__init__(BrickletRotaryEncoderV2, *args)

        self.re = self.device

        self.cbe_count = CallbackEmulator(functools.partial(self.re.get_count, False),
                                          self.cb_count,
                                          self.increase_error_count)

        self.qtcb_pressed.connect(self.cb_pressed)
        self.re.register_callback(self.re.CALLBACK_PRESSED,
                                  self.qtcb_pressed.emit)

        self.qtcb_released.connect(self.cb_released)
        self.re.register_callback(self.re.CALLBACK_RELEASED,
                                  self.qtcb_released.emit)

        self.reset_button = QPushButton('Reset Count')
        self.reset_button.clicked.connect(self.reset_clicked)

        self.encoder_knob = KnobWidget(self)
        self.encoder_knob.setFocusPolicy(Qt.NoFocus)
        self.encoder_knob.set_total_angle(360)
        self.encoder_knob.set_range(0, 24)
        self.encoder_knob.set_scale(2, 2)
        self.encoder_knob.set_scale_text_visible(False)
        self.encoder_knob.set_scale_arc_visible(False)
        self.encoder_knob.set_knob_radius(25)
        self.encoder_knob.set_value(0)

        self.current_count = CurveValueWrapper()

        plots = [('Count', Qt.red, self.current_count, str)]
        self.plot_widget = PlotWidget('Count', plots, update_interval=0.025, y_resolution=1.0)

        vlayout = QVBoxLayout()
        vlayout.addStretch()
        vlayout.addWidget(self.encoder_knob)
        vlayout.addWidget(self.reset_button)
        vlayout.addStretch()

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addLayout(vlayout)

    def cb_released(self):
        self.encoder_knob.set_pressed(False)

    def cb_pressed(self):
        self.encoder_knob.set_pressed(True)

    def cb_count(self, count):
        self.current_count.value = count
        self.encoder_knob.set_value((count + 12) % 24)

    def reset_clicked(self):
        async_call(self.re.get_count, True, None, self.increase_error_count)
        self.cb_count(0)

    def start(self):
        async_call(self.re.get_count, False, self.cb_count, self.increase_error_count)
        async_call(self.re.is_pressed, None, self.encoder_knob.set_pressed, self.increase_error_count)

        self.cbe_count.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_count.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryEncoderV2.DEVICE_IDENTIFIER
