# -*- coding: utf-8 -*-
"""
LED Strip Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

led_strip.py: LED Strip Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_led_strip import BrickletLEDStrip
from brickv.async_call import async_call

from brickv.plugin_system.plugins.led_strip.ui_led_strip import Ui_LEDStrip

from PyQt4.QtCore import pyqtSignal, QTimer

import colorsys

class LEDStrip(PluginBase, Ui_LEDStrip):
    qtcb_frame_rendered = pyqtSignal(int)

    STATE_IDLE = 0
    STATE_COLOR_SINGLE = 1
    STATE_COLOR_BLACK = 2
    STATE_COLOR_GRADIENT = 3
    STATE_COLOR_DOT = 4

    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'LED Strip Bricklet', version, BrickletLEDStrip)

        self.setupUi(self)

        self.led_strip = self.device

        self.has_clock_frequency = version >= (2, 0, 1)
        self.has_chip_type = version >= (2, 0, 2)

        self.qtcb_frame_rendered.connect(self.cb_frame_rendered)

        self.button_color.pressed.connect(self.color_pressed)
        self.button_black.pressed.connect(self.black_pressed)
        self.button_gradient.pressed.connect(self.gradient_pressed)
        self.button_dot.pressed.connect(self.dot_pressed)
        self.box_frame_duration.valueChanged.connect(self.frame_duration_changed)

        if self.has_clock_frequency:
            self.box_clock_frequency.valueChanged.connect(self.clock_frequency_changed)
        else:
            self.box_clock_frequency.setValue(20000000)
            self.box_clock_frequency.setEnabled(False)

        if self.has_chip_type:
            self.chip_type_combobox.currentIndexChanged.connect(self.chip_type_index_changed)
        else:
            self.chip_type_label.setText("Chip Type (needs FW >= 2.0.2)")
            self.chip_type_combobox.setCurrentIndex(0)
            self.chip_type_combobox.setEnabled(False)

        self.state = self.STATE_IDLE

        self.gradient_counter = 0
        self.dot_counter = 0
        self.dot_direction = 1

        self.voltage = 0

        self.voltage_timer = QTimer()
        self.voltage_timer.timeout.connect(self.update_voltage)
        self.voltage_timer.setInterval(1000)

    def chip_type_index_changed(self, index, only_config = False):
        chip = 2801
        if index == 0:
            chip = 2801
            self.box_clock_frequency.show()
            self.label_clock_frequency.show()
        elif index == 1:
            chip = 2811
            self.box_clock_frequency.hide()
            self.label_clock_frequency.hide()
        elif index == 2:
            chip = 2812
            self.box_clock_frequency.hide()
            self.label_clock_frequency.hide()

        if not only_config:
            self.led_strip.set_chip_type(chip)

    def update_voltage(self):
        async_call(self.led_strip.get_supply_voltage, None, self.cb_voltage, self.increase_error_count)

    def cb_chip_type(self, chip):
        if chip == 2801:
            self.chip_type_combobox.setCurrentIndex(0)
            self.chip_type_index_changed(0, True)
        elif chip == 2811:
            self.chip_type_combobox.setCurrentIndex(1)
            self.chip_type_index_changed(1, True)
        elif chip == 2812:
            self.chip_type_combobox.setCurrentIndex(2)
            self.chip_type_index_changed(2, True)

    def cb_frequency(self, frequency):
        self.box_clock_frequency.setValue(frequency)

    def cb_voltage(self, voltage):
        self.label_voltage.setText(str(voltage/1000.0) + 'V')

    def cb_frame_rendered(self):
        if self.state == self.STATE_COLOR_SINGLE:
            self.render_color_single()
        elif self.state == self.STATE_COLOR_BLACK:
            self.render_color_black()
        elif self.state == self.STATE_COLOR_GRADIENT:
            self.render_color_gradient()
        elif self.state == self.STATE_COLOR_DOT:
            self.render_color_dot()

    def clock_frequency_changed(self, frequency):
        self.led_strip.set_clock_frequency(frequency)

    def frame_duration_changed(self, duration):
        self.led_strip.set_frame_duration(duration)

    def color_pressed(self):
        old_state = self.state
        self.state = self.STATE_COLOR_SINGLE
        if old_state == self.STATE_IDLE:
            self.render_color_single()

    def black_pressed(self):
        old_state = self.state
        self.state = self.STATE_COLOR_BLACK
        if old_state == self.STATE_IDLE:
            self.render_color_black()

    def gradient_pressed(self):
        old_state = self.state
        self.state = self.STATE_COLOR_GRADIENT
        if old_state == self.STATE_IDLE:
            self.render_color_gradient()

    def dot_pressed(self):
        self.dot_counter = 0
        self.dot_direction = 1
        old_state = self.state
        self.state = self.STATE_COLOR_DOT
        if old_state == self.STATE_IDLE:
            self.render_color_dot()

    def render_color_single(self):
        num_leds = self.box_num_led.value()

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        i = 0

        while num_leds > 0:
            num_leds -= 16
            if num_leds < 0:
                leds = 16 + num_leds
            else:
                leds = 16

            r_val = [r]*leds
            r_val.extend([0]*(16 - leds))
            g_val = [g]*leds
            g_val.extend([0]*(16 - leds))
            b_val = [b]*leds
            b_val.extend([0]*(16 - leds))

            self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            i += leds

    def render_color_black(self):
        num_leds = self.box_num_led.value()

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        i = 0

        while num_leds > 0:
            num_leds -= 16
            if num_leds < 0:
                leds = 16 + num_leds
            else:
                leds = 16

            r_val = [0]*leds
            r_val.extend([0]*(16 - leds))
            g_val = [0]*leds
            g_val.extend([0]*(16 - leds))
            b_val = [0]*leds
            b_val.extend([0]*(16 - leds))

            self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            i += leds

    def render_color_gradient(self):
        num_leds = self.box_num_led.value()
        self.gradient_counter += max(num_leds, 16) * self.box_speed.value() / 100.0 / 4.0
        ra = []
        ga = []
        ba = []

        range_leds_len = max(num_leds, 16)
        range_leds = range(range_leds_len)
        range_leds = range_leds[int(self.gradient_counter) % range_leds_len:] + range_leds[:int(self.gradient_counter) % range_leds_len]
        range_leds = reversed(range_leds)

        for i in range_leds:
            r, g, b = colorsys.hsv_to_rgb(1.0*i/range_leds_len, 1, 0.1)
            ra.append(int(r*255))
            ga.append(int(g*255))
            ba.append(int(b*255))

        i = 0
        while num_leds > 0:
            num_leds -= 16
            if num_leds < 0:
                leds = 16 + num_leds
            else:
                leds = 16

            r_val = ra[:leds]
            r_val.extend([0]*(16 - leds))
            g_val = ga[:leds]
            g_val.extend([0]*(16 - leds))
            b_val = ba[:leds]
            b_val.extend([0]*(16 - leds))

            try:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            except:
                pass

            ra = ra[leds:]
            ga = ga[leds:]
            ba = ba[leds:]
            i += leds

    def render_color_dot(self):
        num_leds = self.box_num_led.value()
        self.dot_counter = self.dot_counter % num_leds

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        i = 0
        while num_leds > 0:
            num_leds -= 16
            if num_leds < 0:
                leds = 16 + num_leds
            else:
                leds = 16

            r_val = [0]*leds
            r_val.extend([0]*(16 - leds))
            g_val = [0]*leds
            g_val.extend([0]*(16 - leds))
            b_val = [0]*leds
            b_val.extend([0]*(16 - leds))

            if self.dot_counter >= i and self.dot_counter < i + 16:
                k = self.dot_counter % 16
                r_val[k] = r
                g_val[k] = g
                b_val[k] = b

            self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            i += leds

        self.dot_counter += self.dot_direction * self.box_speed.value()

        num_leds = self.box_num_led.value()
        if self.dot_counter >= num_leds:
            self.dot_direction = -1
            self.dot_counter = num_leds - 1
        elif self.dot_counter < 0:
            self.dot_direction = 1
            self.dot_counter = 0

    def start(self):
        if self.has_chip_type:
            async_call(self.led_strip.get_chip_type, None, self.cb_chip_type, self.increase_error_count)
        if self.has_clock_frequency:
            async_call(self.led_strip.get_clock_frequency, None, self.cb_frequency, self.increase_error_count)
        async_call(self.led_strip.get_supply_voltage, None, self.cb_voltage, self.increase_error_count)
        self.voltage_timer.start()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED,
                                         self.qtcb_frame_rendered.emit)

    def stop(self):
        self.voltage_timer.stop()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED, None)

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'led_strip'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLEDStrip.DEVICE_IDENTIFIER
