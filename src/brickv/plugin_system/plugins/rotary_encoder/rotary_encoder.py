# -*- coding: utf-8 -*-
"""
Rotary Encoder Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

rotary_encoder.py: Rotary Encoder Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QPushButton

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_rotary_encoder import BrickletRotaryEncoder
from brickv.knob_widget import KnobWidget
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class RotaryEncoder(PluginBase):
    qtcb_pressed = pyqtSignal()
    qtcb_released = pyqtSignal()

    def __init__(self, *args):
        super().__init__(BrickletRotaryEncoder, *args)

        self.re = self.device

        # the firmware version of a EEPROM Bricklet can (under common circumstances)
        # not change during the lifetime of an EEPROM Bricklet plugin. therefore,
        # it's okay to make final decisions based on it here
        self.has_fixed_is_pressed = self.firmware_version >= (2, 0, 2) # is_pressed return value was inverted before

        self.cbe_count = CallbackEmulator(self,
                                          self.get_count,
                                          False,
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

    def get_count(self, reset):
        count = self.re.get_count(reset)

        return 0 if reset else count

    def reset_clicked(self):
        async_call(self.get_count, True, self.cb_count, self.increase_error_count)

    def is_pressed_async(self, is_pressed):
        if self.has_fixed_is_pressed:
            self.encoder_knob.set_pressed(is_pressed)
        else:
            self.encoder_knob.set_pressed(not is_pressed)

    def start(self):
        async_call(self.re.is_pressed, None, self.is_pressed_async, self.increase_error_count)

        self.cbe_count.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_count.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRotaryEncoder.DEVICE_IDENTIFIER
