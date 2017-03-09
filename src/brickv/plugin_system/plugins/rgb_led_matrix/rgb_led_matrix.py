# -*- coding: utf-8 -*-
"""
RGB LED Matrix Plugin
Copyright (C) 2015-2017 Olaf Lüke <olaf@tinkerforge.com>

rgb_led_matrix.py: RGB LED Matrix Plugin Implementation

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

import colorsys

from PyQt4.QtCore import pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.rgb_led_matrix.ui_rgb_led_matrix import Ui_RGBLEDMatrix
from brickv.bindings.bricklet_rgb_led_matrix import BrickletRGBLEDMatrix
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

NUM_LEDS = 64

class RGBLEDMatrix(COMCUPluginBase, Ui_RGBLEDMatrix):
    qtcb_frame_started = pyqtSignal(int)

    STATE_IDLE = 0
    STATE_COLOR_SINGLE = 1
    STATE_COLOR_BLACK = 2
    STATE_COLOR_GRADIENT = 3
    STATE_COLOR_DOT = 4

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRGBLEDMatrix, *args)

        self.setupUi(self)

        self.rgb_led_matrix = self.device

        self.qtcb_frame_started.connect(self.cb_frame_started)

        self.button_color.clicked.connect(self.color_clicked)
        self.button_black.clicked.connect(self.black_clicked)
        self.button_gradient.clicked.connect(self.gradient_clicked)
        self.button_dot.clicked.connect(self.dot_clicked)
        self.box_frame_duration.valueChanged.connect(self.frame_duration_changed)

        self.state = self.STATE_IDLE

        self.gradient_counter = 0
        self.dot_counter = 0
        self.dot_direction = 1

        self.voltage = 0
        
        self.cbe_supply_voltage = CallbackEmulator(self.rgb_led_matrix.get_supply_voltage,
                                                   self.cb_supply_voltage,
                                                   self.increase_error_count)

    def set_rgb(self, r, g, b):
        async_call(self.rgb_led_matrix.set_red, r, None, self.increase_error_count)
        async_call(self.rgb_led_matrix.set_green, g, None, self.increase_error_count)
        async_call(self.rgb_led_matrix.set_blue, b, None, self.increase_error_count)

    def cb_supply_voltage(self, voltage):
        self.label_voltage.setText(str(voltage/1000.0) + 'V')

    def cb_frame_started(self):
        if self.state == self.STATE_COLOR_SINGLE:
            self.render_color_single()
        elif self.state == self.STATE_COLOR_BLACK:
            self.render_color_black()
        elif self.state == self.STATE_COLOR_GRADIENT:
            self.render_color_gradient()
        elif self.state == self.STATE_COLOR_DOT:
            self.render_color_dot()

    def frame_duration_changed(self, duration):
#        self.rgb_led_matrix.set_frame_duration(duration)
        async_call(self.rgb_led_matrix.set_frame_duration, duration, None, self.increase_error_count)
    
    def color_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_SINGLE
        if old_state == self.STATE_IDLE:
            self.render_color_single()

    def black_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_BLACK
        if old_state == self.STATE_IDLE:
            self.render_color_black()

    def gradient_clicked(self):
        old_state = self.state
        self.state = self.STATE_COLOR_GRADIENT
        if old_state == self.STATE_IDLE:
            self.render_color_gradient()

    def dot_clicked(self):
        self.dot_counter = 0
        self.dot_direction = 1
        old_state = self.state
        self.state = self.STATE_COLOR_DOT
        if old_state == self.STATE_IDLE:
            self.render_color_dot()

    def render_color_single(self):
        self.set_rgb([self.box_r.value()]*NUM_LEDS, [self.box_g.value()]*NUM_LEDS, [self.box_b.value()]*NUM_LEDS)
        
    def render_color_black(self):
        value = [0]*NUM_LEDS
        self.set_rgb(value, value, value)
        
    def render_color_gradient(self):
        self.gradient_counter += NUM_LEDS * self.box_speed.value() / 100.0 / 4.0
        ra = []
        ga = []
        ba = []

        range_leds = range(NUM_LEDS)
        range_leds = range_leds[int(self.gradient_counter) % NUM_LEDS:] + range_leds[:int(self.gradient_counter) % NUM_LEDS]
        range_leds = reversed(range_leds)

        for i in range_leds:
            r, g, b = colorsys.hsv_to_rgb(1.0*i/NUM_LEDS, 1, 0.1)
            ra.append(int(r*255))
            ga.append(int(g*255))
            ba.append(int(b*255))

        self.set_rgb(ra, ga, ba)

    def render_color_dot(self):
        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        self.dot_counter = self.dot_counter % NUM_LEDS

        r_val = [0]*NUM_LEDS
        g_val = [0]*NUM_LEDS
        b_val = [0]*NUM_LEDS

        r_val[self.dot_counter] = r
        g_val[self.dot_counter] = g
        b_val[self.dot_counter] = b

        self.set_rgb(r_val, g_val, b_val)

        self.dot_counter += self.dot_direction * self.box_speed.value()

        if self.dot_counter >= NUM_LEDS:
            self.dot_direction = -1
            self.dot_counter = NUM_LEDS - 1
        elif self.dot_counter < 0:
            self.dot_direction = 1
            self.dot_counter = 0

    def start(self):
        self.rgb_led_matrix.register_callback(self.rgb_led_matrix.CALLBACK_FRAME_STARTED, self.qtcb_frame_started.emit)
        self.cbe_supply_voltage.set_period(250)
        async_call(self.rgb_led_matrix.set_frame_duration, self.box_frame_duration.value(), None, self.increase_error_count)

    def stop(self):
        self.rgb_led_matrix.register_callback(self.rgb_led_matrix.CALLBACK_FRAME_STARTED, None)
        self.cbe_supply_voltage.set_period(0)
        async_call(self.rgb_led_matrix.set_frame_duration, 0, None, self.increase_error_count)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rgb_led_matrix'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRGBLEDMatrix.DEVICE_IDENTIFIER
