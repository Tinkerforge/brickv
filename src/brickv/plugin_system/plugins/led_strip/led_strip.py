# -*- coding: utf-8 -*-
"""
LED Strip Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

ToDo: The frame duration is set by the last set value. The displayed 100
does not have to be correct!
"""

import colorsys

from PyQt4.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.led_strip.ui_led_strip import Ui_LEDStrip
from brickv.bindings.bricklet_led_strip import BrickletLEDStrip
from brickv.async_call import async_call

class LEDStrip(PluginBase, Ui_LEDStrip):
    qtcb_frame_rendered = pyqtSignal(int)

    STATE_IDLE = 0
    STATE_COLOR_SINGLE = 1
    STATE_COLOR_BLACK = 2
    STATE_COLOR_GRADIENT = 3
    STATE_COLOR_DOT = 4

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLEDStrip, *args)

        self.setupUi(self)

        self.led_strip = self.device

        self.has_clock_frequency = self.firmware_version >= (2, 0, 1)
        self.has_chip_type = self.firmware_version >= (2, 0, 2)
        self.has_rgbw = self.firmware_version >= (2, 0, 6)
        self.has_more_chip_types = self.firmware_version >= (2, 0, 6)
        self.has_channel_mapping = self.firmware_version >= (2, 0, 6)

        self.qtcb_frame_rendered.connect(self.cb_frame_rendered)

        self.button_color.clicked.connect(self.color_clicked)
        self.button_black.clicked.connect(self.black_clicked)
        self.button_gradient.clicked.connect(self.gradient_clicked)
        self.button_dot.clicked.connect(self.dot_clicked)
        self.box_frame_duration.valueChanged.connect(self.frame_duration_changed)
        self.gradient_intensity.valueChanged.connect(self.gradient_intensity_changed)

        if self.has_clock_frequency:
            self.box_clock_frequency.valueChanged.connect(self.clock_frequency_changed)
        else:
            self.box_clock_frequency.setValue(20000000)
            self.box_clock_frequency.setEnabled(False)

        if self.has_chip_type:
            self.chip_type_combobox.currentIndexChanged.connect(self.chip_type_index_changed)
        else:
            self.chip_type_label.setText("Chip Type (FW Version >= 2.0.2 required)")
            self.chip_type_combobox.setCurrentIndex(0)
            self.chip_type_combobox.setEnabled(False)
            
        if self.has_rgbw:
            self.box_w.setDisabled(True)
        else:
            self.box_w.setDisabled(True)

        if self.has_more_chip_types:
            self.label_chip_type_note.setText(" ")
            self.chip_type_combobox.addItem("LPD8806")
            self.chip_type_combobox.addItem("APA102")
        else:
            self.label_chip_type_note.setText("FW >= 2.0.6 required for more chip types")

        if self.has_channel_mapping:
            self.channel_mapping_combobox.currentIndexChanged.connect(self.channel_mapping_changed)
        else:
            self.channel_mapping_combobox.setCurrentIndex(0)
            self.channel_mapping_combobox.setEnabled(False)

        self.state = self.STATE_IDLE

        self.gradient_counter = 0
        self.dot_counter = 0
        self.dot_direction = 1

        self.voltage = 0

        self.voltage_timer = QTimer()
        self.voltage_timer.timeout.connect(self.update_voltage)
        self.voltage_timer.setInterval(1000)

    def channel_mapping_changed(self, index, only_config=False):
        self.led_strip.set_channel_mapping(self.channel_mapping_combobox.currentIndex())
        if self.channel_mapping_combobox.currentIndex() > 5:
            self.box_w.setDisabled(False)
        else:
            self.box_w.setDisabled(True)

    def chip_type_index_changed(self, index, only_config=False):
        chip = 2801
        if index == 0:
            chip = 2801
            self.box_clock_frequency.show()
            self.label_clock_frequency.show()
            self.box_w.hide()
            self.label_7.hide()
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif index == 1:
            chip = 2811
            self.box_clock_frequency.hide()
            self.label_clock_frequency.hide()
            self.box_w.hide()
            self.label_7.hide()
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif index == 2:
            chip = 2812
            self.box_clock_frequency.hide()
            self.label_clock_frequency.hide()
            self.box_w.show()
            self.label_7.show()
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif index == 3:
            chip = 8806
            self.box_clock_frequency.show()
            self.label_clock_frequency.show()
            self.box_w.hide()
            self.label_7.hide()
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif index == 4:
            chip = 102
            self.box_clock_frequency.show()
            self.label_clock_frequency.show()
            self.box_w.hide()
            self.label_7.hide()
            self.brightness_slider.show()
            self.brightness_label.show();

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
        elif chip == 8806:
            self.chip_type_combobox.setCurrentIndex(3)
            self.chip_type_index_changed(3, True)
        elif chip == 102:
            self.chip_type_combobox.setCurrentIndex(4)
            self.chip_type_index_changed(4, True)

    def cb_frequency(self, frequency):
        self.box_clock_frequency.setValue(frequency)

    def cb_duration(self, duration):
        self.box_frame_duration.setValue(duration)

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

    def cb_channel_mapping(self, channel_mapping):
        self.channel_mapping_combobox.setCurrentIndex(channel_mapping)

    def clock_frequency_changed(self, frequency):
        self.led_strip.set_clock_frequency(frequency)

    def frame_duration_changed(self, duration):
        self.led_strip.set_frame_duration(duration)

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

    def gradient_intensity_changed(self):
        self.label_gradient_intensity.setText(str(self.gradient_intensity.value()) + '%')

    def render_color_single(self):
        num_leds = self.box_num_led.value()

        if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
            ledBlock = 12
        elif self.chip_type_combobox.currentIndex() == 4:
            ledBlock = 12
        else:
            ledBlock = 16

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()
        if self.chip_type_combobox.currentIndex() == 4:
            w = self.brightness_slider.value()
        else:
            w = self.box_w.value()

        i = 0

        while num_leds > 0:
            num_leds -= ledBlock
            if num_leds < 0:
                leds = ledBlock + num_leds
            else:
                leds = ledBlock

            r_val = [r]*leds
            r_val.extend([0]*(ledBlock - leds))
            g_val = [g]*leds
            g_val.extend([0]*(ledBlock - leds))
            b_val = [b]*leds
            b_val.extend([0]*(ledBlock - leds))
            w_val = [w]*leds
            w_val.extend([0]*(ledBlock - leds))

            if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            elif self.chip_type_combobox.currentIndex() == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            else:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            i += leds

    def render_color_black(self):
        num_leds = self.box_num_led.value()
        i = 0

        if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
            ledBlock = 12
        elif self.chip_type_combobox.currentIndex() == 4:
            ledBlock = 12
        else:
            ledBlock = 16

        while num_leds > 0:
            num_leds -= ledBlock
            if num_leds < 0:
                leds = ledBlock + num_leds
            else:
                leds = ledBlock

            r_val = [0]*leds
            r_val.extend([0]*(ledBlock - leds))
            g_val = [0]*leds
            g_val.extend([0]*(ledBlock - leds))
            b_val = [0]*leds
            b_val.extend([0]*(ledBlock - leds))
            w_val = [0]*leds
            w_val.extend([0]*(ledBlock - leds))

            if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            elif self.chip_type_combobox.currentIndex() == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            else:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)
            i += leds

    def render_color_gradient(self):
        num_leds = self.box_num_led.value()
        if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
            ledBlock = 12
        elif self.chip_type_combobox.currentIndex() == 4:
            ledBlock = 12
            brightness = self.brightness_slider.value()
        else:
            ledBlock = 16

        self.gradient_counter += max(num_leds, ledBlock) * self.box_speed.value() / 100.0 / 4.0
        ra = []
        ga = []
        ba = []

        range_leds_len = max(num_leds, ledBlock)
        range_leds = range(range_leds_len)
        range_leds = range_leds[int(self.gradient_counter) % range_leds_len:] + range_leds[:int(self.gradient_counter) % range_leds_len]
        range_leds = reversed(range_leds)

        intensity = (self.gradient_intensity.value()/100.0)
        self.label_gradient_intensity.setText(str(self.gradient_intensity.value()) + '%')

        for i in range_leds:
            r, g, b = colorsys.hsv_to_rgb(1.0*i/range_leds_len, 1, intensity)
            ra.append(int(r*255))
            ga.append(int(g*255))
            ba.append(int(b*255))

        i = 0

        while num_leds > 0:
            num_leds -= ledBlock
            
            if num_leds < 0:
                leds = ledBlock + num_leds
            else:
                leds = ledBlock

            r_val = ra[:leds]
            r_val.extend([0]*(ledBlock - leds))
            g_val = ga[:leds]
            g_val.extend([0]*(ledBlock - leds))
            b_val = ba[:leds]
            b_val.extend([0]*(ledBlock - leds))
            if self.chip_type_combobox.currentIndex() == 4:
               brightness_val = [brightness]*leds
               brightness_val.extend([0]*(ledBlock - leds))

            if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, [0]*12)
            elif self.chip_type_combobox.currentIndex() == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, brightness_val)
            else:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)

            ra = ra[leds:]
            ga = ga[leds:]
            ba = ba[leds:]
            i += leds

    def render_color_dot(self):
        num_leds = self.box_num_led.value()
        self.dot_counter = self.dot_counter % num_leds

        if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
            ledBlock = 12
        elif self.chip_type_combobox.currentIndex() == 4:
            ledBlock = 12
        else:
            ledBlock = 16

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()
        if self.chip_type_combobox.currentIndex() == 4:
            w = self.brightness_slider.value()
        else:
            w = self.box_w.value()

        i = 0
        while num_leds > 0:
            num_leds -= ledBlock
            if num_leds < 0:
                leds = ledBlock + num_leds
            else:
                leds = ledBlock

            r_val = [0]*leds
            r_val.extend([0]*(ledBlock - leds))
            g_val = [0]*leds
            g_val.extend([0]*(ledBlock - leds))
            b_val = [0]*leds
            b_val.extend([0]*(ledBlock - leds))
            if self.chip_type_combobox.currentIndex() == 4:
                w_val = [w]*leds
                w_val.extend([0]*(ledBlock - leds))
            else:
                w_val = [0]*leds
                w_val.extend([0]*(ledBlock - leds))

            if self.dot_counter >= i and self.dot_counter < i + ledBlock:
                k = self.dot_counter % ledBlock
                r_val[k] = r
                g_val[k] = g
                b_val[k] = b
                w_val[k] = w

            if self.channel_mapping_combobox.currentIndex() > 5 and self.chip_type_combobox.currentIndex() == 2:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            elif self.chip_type_combobox.currentIndex() == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            else:
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
        if self.has_channel_mapping:
            async_call(self.led_strip.get_channel_mapping, None, self.cb_channel_mapping, self.increase_error_count)
        async_call(self.led_strip.get_supply_voltage, None, self.cb_voltage, self.increase_error_count)
        async_call(self.led_strip.get_frame_duration, None, self.cb_duration, self.increase_error_count)
        self.voltage_timer.start()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED,
                                         self.qtcb_frame_rendered.emit)

    def stop(self):
        self.voltage_timer.stop()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED, None)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'led_strip'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLEDStrip.DEVICE_IDENTIFIER
