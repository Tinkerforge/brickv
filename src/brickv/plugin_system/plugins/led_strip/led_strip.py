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
        self.has_more_chip_types = self.firmware_version >= (2, 0, 6)
        self.has_channel_mapping = self.firmware_version >= (2, 0, 6)
        self.has_configurable_rame_rendered_callback = self.firmware_version >= (2, 0, 6)

        self.frame_read_callback_was_enabled = False

        self.qtcb_frame_rendered.connect(self.cb_frame_rendered)

        self.button_color.clicked.connect(self.color_clicked)
        self.button_black.clicked.connect(self.black_clicked)
        self.button_gradient.clicked.connect(self.gradient_clicked)
        self.button_dot.clicked.connect(self.dot_clicked)
        self.box_frame_duration.valueChanged.connect(self.frame_duration_changed)
        self.gradient_intensity.valueChanged.connect(self.gradient_intensity_changed)

        self.chip_type_combobox.addItem('WS2801', (BrickletLEDStrip.CHIP_TYPE_WS2801, 3))
        self.chip_type_combobox.addItem('WS2811', (BrickletLEDStrip.CHIP_TYPE_WS2811, 3))
        self.chip_type_combobox.addItem('WS2812 / SK6812 / NeoPixel RGB (GRB)', (BrickletLEDStrip.CHIP_TYPE_WS2812, 3))

        if self.has_clock_frequency:
            self.box_clock_frequency.editingFinished.connect(self.clock_frequency_changed)
        else:
            self.box_clock_frequency.setValue(20000000)
            self.box_clock_frequency.setEnabled(False)

        if self.has_chip_type:
            self.chip_type_combobox.currentIndexChanged.connect(self.chip_type_changed)
        else:
            self.chip_type_label.setText("Chip Type (FW Version >= 2.0.2 required)")
            self.chip_type_combobox.setCurrentIndex(0)
            self.chip_type_combobox.setEnabled(False)

        if self.has_more_chip_types:
            self.chip_type_combobox.addItem('SK6812RGBW / NeoPixel RGBW (GRBW)', (BrickletLEDStrip.CHIP_TYPE_WS2812, 4))
            self.chip_type_combobox.addItem('LPD8806', (BrickletLEDStrip.CHIP_TYPE_LPD8806, 3))
            self.chip_type_combobox.addItem('APA102 / DotStar (bBGR)', (BrickletLEDStrip.CHIP_TYPE_APA102, 4))
        elif self.has_chip_type:
            self.chip_type_label.setText("Chip Type (FW Version >= 2.0.6 required for more chip types)")

        if self.has_channel_mapping:
            self.channel_mapping_combobox.currentIndexChanged.connect(self.channel_mapping_changed)
        else:
            self.channel_mapping_label.setText("Channel Mapping (FW Version >= 2.0.6 required)")
            self.channel_mapping_combobox.setCurrentIndex(3) # BGR
            self.channel_mapping_combobox.setEnabled(False)

        self.state = self.STATE_IDLE

        self.gradient_counter = 0
        self.dot_counter = 0
        self.dot_direction = 1

        self.voltage = 0

        self.voltage_timer = QTimer()
        self.voltage_timer.timeout.connect(self.update_voltage)
        self.voltage_timer.setInterval(1000)

        self.chip_type_changed(0, ui_only=True)

    def channel_mapping_changed(self, index):
        if index < 0:
            return

        channel_mapping = self.channel_mapping_combobox.itemData(index)

        self.led_strip.set_channel_mapping(channel_mapping)

    def chip_type_changed(self, index, ui_only=False):
        chip_type, num_channels = self.chip_type_combobox.itemData(index)

        has_clock = True

        if chip_type == BrickletLEDStrip.CHIP_TYPE_WS2801:
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif chip_type == BrickletLEDStrip.CHIP_TYPE_WS2811:
            has_clock = False
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif chip_type == BrickletLEDStrip.CHIP_TYPE_WS2812:
            has_clock = False
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif chip_type == BrickletLEDStrip.CHIP_TYPE_LPD8806:
            self.brightness_slider.hide()
            self.brightness_label.hide()
        elif chip_type == BrickletLEDStrip.CHIP_TYPE_APA102:
            self.brightness_slider.show()
            self.brightness_label.show()

        self.box_clock_frequency.setVisible(has_clock)
        self.label_clock_frequency.setVisible(has_clock)
        self.box_w.setVisible(chip_type != BrickletLEDStrip.CHIP_TYPE_APA102 and num_channels == 4)
        self.label_w.setVisible(chip_type != BrickletLEDStrip.CHIP_TYPE_APA102 and num_channels == 4)

        if not ui_only:
            self.led_strip.set_chip_type(chip_type)

        channel_mapping = self.channel_mapping_combobox.itemData(self.channel_mapping_combobox.currentIndex())

        self.channel_mapping_combobox.blockSignals(True)
        self.channel_mapping_combobox.clear()

        if num_channels == 3:
            self.channel_mapping_combobox.addItem('RGB', BrickletLEDStrip.CHANNEL_MAPPING_RGB)
            self.channel_mapping_combobox.addItem('RBG', BrickletLEDStrip.CHANNEL_MAPPING_RBG)
            self.channel_mapping_combobox.addItem('BRG', BrickletLEDStrip.CHANNEL_MAPPING_BRG)
            self.channel_mapping_combobox.addItem('BGR', BrickletLEDStrip.CHANNEL_MAPPING_BGR)
            self.channel_mapping_combobox.addItem('GRB', BrickletLEDStrip.CHANNEL_MAPPING_GRB)
            self.channel_mapping_combobox.addItem('GBR', BrickletLEDStrip.CHANNEL_MAPPING_GBR)

            self.channel_mapping_combobox.setCurrentIndex(3) # BGR, default for disabled
        else:
            if chip_type == BrickletLEDStrip.CHIP_TYPE_APA102:
                self.channel_mapping_combobox.addItem('bRGB', BrickletLEDStrip.CHANNEL_MAPPING_WRGB)
                self.channel_mapping_combobox.addItem('bRBG', BrickletLEDStrip.CHANNEL_MAPPING_WRBG)
                self.channel_mapping_combobox.addItem('bBRG', BrickletLEDStrip.CHANNEL_MAPPING_WBRG)
                self.channel_mapping_combobox.addItem('bBGR', BrickletLEDStrip.CHANNEL_MAPPING_WBGR)
                self.channel_mapping_combobox.addItem('bGRB', BrickletLEDStrip.CHANNEL_MAPPING_WGRB)
                self.channel_mapping_combobox.addItem('bGBR', BrickletLEDStrip.CHANNEL_MAPPING_WGBR)
            else:
                self.channel_mapping_combobox.addItem('RGBW', BrickletLEDStrip.CHANNEL_MAPPING_RGBW)
                self.channel_mapping_combobox.addItem('RGWB', BrickletLEDStrip.CHANNEL_MAPPING_RGWB)
                self.channel_mapping_combobox.addItem('RBGW', BrickletLEDStrip.CHANNEL_MAPPING_RBGW)
                self.channel_mapping_combobox.addItem('RBWG', BrickletLEDStrip.CHANNEL_MAPPING_RBWG)
                self.channel_mapping_combobox.addItem('RWGB', BrickletLEDStrip.CHANNEL_MAPPING_RWGB)
                self.channel_mapping_combobox.addItem('RWBG', BrickletLEDStrip.CHANNEL_MAPPING_RWBG)
                self.channel_mapping_combobox.addItem('GRWB', BrickletLEDStrip.CHANNEL_MAPPING_GRWB)
                self.channel_mapping_combobox.addItem('GRBW', BrickletLEDStrip.CHANNEL_MAPPING_GRBW)
                self.channel_mapping_combobox.addItem('GBWR', BrickletLEDStrip.CHANNEL_MAPPING_GBWR)
                self.channel_mapping_combobox.addItem('GBRW', BrickletLEDStrip.CHANNEL_MAPPING_GBRW)
                self.channel_mapping_combobox.addItem('GWBR', BrickletLEDStrip.CHANNEL_MAPPING_GWBR)
                self.channel_mapping_combobox.addItem('GWRB', BrickletLEDStrip.CHANNEL_MAPPING_GWRB)
                self.channel_mapping_combobox.addItem('BRGW', BrickletLEDStrip.CHANNEL_MAPPING_BRGW)
                self.channel_mapping_combobox.addItem('BRWG', BrickletLEDStrip.CHANNEL_MAPPING_BRWG)
                self.channel_mapping_combobox.addItem('BGRW', BrickletLEDStrip.CHANNEL_MAPPING_BGRW)
                self.channel_mapping_combobox.addItem('BGWR', BrickletLEDStrip.CHANNEL_MAPPING_BGWR)
                self.channel_mapping_combobox.addItem('BWRG', BrickletLEDStrip.CHANNEL_MAPPING_BWRG)
                self.channel_mapping_combobox.addItem('BWGR', BrickletLEDStrip.CHANNEL_MAPPING_BWGR)
                self.channel_mapping_combobox.addItem('WRBG', BrickletLEDStrip.CHANNEL_MAPPING_WRBG)
                self.channel_mapping_combobox.addItem('WRGB', BrickletLEDStrip.CHANNEL_MAPPING_WRGB)
                self.channel_mapping_combobox.addItem('WGBR', BrickletLEDStrip.CHANNEL_MAPPING_WGBR)
                self.channel_mapping_combobox.addItem('WGRB', BrickletLEDStrip.CHANNEL_MAPPING_WGRB)
                self.channel_mapping_combobox.addItem('WBGR', BrickletLEDStrip.CHANNEL_MAPPING_WBGR)
                self.channel_mapping_combobox.addItem('WBRG', BrickletLEDStrip.CHANNEL_MAPPING_WBRG)

        self.channel_mapping_combobox.blockSignals(False)

        self.get_channel_mapping_async(channel_mapping)

    def update_voltage(self):
        async_call(self.led_strip.get_supply_voltage, None, self.get_supply_voltage_async, self.increase_error_count)

    def get_chip_type_async(self, new_chip_type):
        for index in range(self.chip_type_combobox.count()):
            chip_type, num_channels = self.chip_type_combobox.itemData(index)

            if chip_type == new_chip_type:
                self.chip_type_combobox.setCurrentIndex(index)
                break

    def get_clock_frequency_async(self, frequency):
        self.box_clock_frequency.setValue(frequency)

    def get_frame_duration_async(self, duration):
        self.box_frame_duration.setValue(duration)

    def get_supply_voltage_async(self, voltage):
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

    def get_channel_mapping_async(self, new_channel_mapping, fuzzy=True):
        available = []

        for index in range(self.channel_mapping_combobox.count()):
            channel_mapping = self.channel_mapping_combobox.itemData(index)
            available.append(channel_mapping)

            if channel_mapping == new_channel_mapping:
                self.channel_mapping_combobox.setCurrentIndex(index)
                return

        if not fuzzy:
            return

        if new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RGB:
            if BrickletLEDStrip.CHANNEL_MAPPING_RGBW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_RGBW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WRGB, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RBG:
            if BrickletLEDStrip.CHANNEL_MAPPING_RBGW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_RBGW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WRBG, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BRG:
            if BrickletLEDStrip.CHANNEL_MAPPING_BRGW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_BRGW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WBRG, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BGR:
            if BrickletLEDStrip.CHANNEL_MAPPING_BGRW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_BGRW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WBGR, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GRB:
            if BrickletLEDStrip.CHANNEL_MAPPING_GRBW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_GRBW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WGRB, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GBR:
            if BrickletLEDStrip.CHANNEL_MAPPING_GBRW in available:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_GBRW, fuzzy=False)
            else:
                self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_WGBR, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RGBW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RGWB or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RWGB or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WRGB:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_RGB, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RBGW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RBWG or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_RWBG or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WRBG:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_RBG, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BRGW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BRWG or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BWRG or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WBRG:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_BRG, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BGRW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BGWR or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_BWGR or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WBGR:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_BGR, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GRBW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GRWB or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GWRB or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WGRB:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_GRB, fuzzy=False)
        elif new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GBRW or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GBWR or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_GWBR or \
             new_channel_mapping == BrickletLEDStrip.CHANNEL_MAPPING_WGBR:
            self.get_channel_mapping_async(BrickletLEDStrip.CHANNEL_MAPPING_GBR, fuzzy=False)

    def clock_frequency_changed(self):
        self.led_strip.set_clock_frequency(self.box_clock_frequency.value())

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

    def render_leds(self, r, g, b, w):
        num_leds = self.box_num_led.value()
        _, num_channels = self.chip_type_combobox.itemData(self.chip_type_combobox.currentIndex())

        if num_channels == 4:
            led_block = 12
        else:
            led_block = 16

        i = 0

        while num_leds > 0:
            num_leds -= led_block

            if num_leds < 0:
                leds = led_block + num_leds
            else:
                leds = led_block

            r_val = r[:leds]
            r_val.extend([0]*(led_block - leds))
            g_val = g[:leds]
            g_val.extend([0]*(led_block - leds))
            b_val = b[:leds]
            b_val.extend([0]*(led_block - leds))
            w_val = w[:leds]
            w_val.extend([0]*(led_block - leds))

            if num_channels == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            else:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)

            i += leds

            r = r[leds:]
            g = g[leds:]
            b = b[leds:]
            w = w[leds:]

    def render_color_single(self):
        num_leds = self.box_num_led.value()
        chip_type, _ = self.chip_type_combobox.itemData(self.chip_type_combobox.currentIndex())

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        if chip_type == BrickletLEDStrip.CHIP_TYPE_APA102:
            w = self.brightness_slider.value() * 8
        else:
            w = self.box_w.value()

        self.render_leds([r]*num_leds, [g]*num_leds, [b]*num_leds, [w]*num_leds)

    def render_color_black(self):
        num_leds = self.box_num_led.value()

        self.render_leds([0]*num_leds, [0]*num_leds, [0]*num_leds, [0]*num_leds)

    def render_color_gradient(self):
        num_leds = self.box_num_led.value()
        brightness = self.brightness_slider.value() * 8
        chip_type, num_channels = self.chip_type_combobox.itemData(self.chip_type_combobox.currentIndex())

        if num_channels == 4:
            led_block = 12
        else:
            led_block = 16

        self.gradient_counter += max(num_leds, led_block) * self.box_speed.value() / 100.0 / 4.0
        ra = []
        ga = []
        ba = []

        range_leds_len = max(num_leds, led_block)
        range_leds = range(range_leds_len)
        range_leds = range_leds[int(self.gradient_counter) % range_leds_len:] + range_leds[:int(self.gradient_counter) % range_leds_len]
        range_leds = reversed(range_leds)

        intensity = self.gradient_intensity.value() / 100.0
        self.label_gradient_intensity.setText(str(self.gradient_intensity.value()) + '%')

        for i in range_leds:
            r, g, b = colorsys.hsv_to_rgb(1.0*i/range_leds_len, 1, intensity)
            ra.append(int(r*255))
            ga.append(int(g*255))
            ba.append(int(b*255))

        i = 0

        while num_leds > 0:
            num_leds -= led_block

            if num_leds < 0:
                leds = led_block + num_leds
            else:
                leds = led_block

            r_val = ra[:leds]
            r_val.extend([0]*(led_block - leds))
            g_val = ga[:leds]
            g_val.extend([0]*(led_block - leds))
            b_val = ba[:leds]
            b_val.extend([0]*(led_block - leds))

            if chip_type == BrickletLEDStrip.CHIP_TYPE_APA102:
                w_val = [brightness]*leds
            else:
                w_val = [0]*leds

            w_val.extend([0]*(led_block - leds))

            if num_channels == 4:
                self.led_strip.set_rgbw_values(i, leds, r_val, g_val, b_val, w_val)
            else:
                self.led_strip.set_rgb_values(i, leds, r_val, g_val, b_val)

            ra = ra[leds:]
            ga = ga[leds:]
            ba = ba[leds:]

            i += leds

    def render_color_dot(self):
        num_leds = self.box_num_led.value()
        chip_type, _ = self.chip_type_combobox.itemData(self.chip_type_combobox.currentIndex())

        r = self.box_r.value()
        g = self.box_g.value()
        b = self.box_b.value()

        if chip_type == BrickletLEDStrip.CHIP_TYPE_APA102:
            w = self.brightness_slider.value() * 8
        else:
            w = self.box_w.value()

        self.dot_counter = self.dot_counter % num_leds

        r_val = [0]*num_leds
        g_val = [0]*num_leds
        b_val = [0]*num_leds
        w_val = [0]*num_leds

        r_val[self.dot_counter] = r
        g_val[self.dot_counter] = g
        b_val[self.dot_counter] = b
        w_val[self.dot_counter] = w

        self.render_leds(r_val, g_val, b_val, w_val)

        self.dot_counter += self.dot_direction * self.box_speed.value()

        if self.dot_counter >= num_leds:
            self.dot_direction = -1
            self.dot_counter = num_leds - 1
        elif self.dot_counter < 0:
            self.dot_direction = 1
            self.dot_counter = 0

    def is_frame_rendered_callback_enabled_async(self, enabled):
        self.frame_rendered_callback_was_enabled = enabled
        self.led_strip.enable_frame_rendered_callback()

    def start(self):
        self.frame_rendered_callback_was_enabled = False

        if self.has_chip_type:
            async_call(self.led_strip.get_chip_type, None, self.get_chip_type_async, self.increase_error_count, log_exception=True)

        if self.has_clock_frequency:
            async_call(self.led_strip.get_clock_frequency, None, self.get_clock_frequency_async, self.increase_error_count, log_exception=True)

        if self.has_channel_mapping:
            async_call(self.led_strip.get_channel_mapping, None, self.get_channel_mapping_async, self.increase_error_count, log_exception=True)

        if self.has_configurable_rame_rendered_callback:
            async_call(self.led_strip.is_frame_rendered_callback_enabled, None, self.is_frame_rendered_callback_enabled_async, self.increase_error_count)

        async_call(self.led_strip.get_supply_voltage, None, self.get_supply_voltage_async, self.increase_error_count, log_exception=True)
        async_call(self.led_strip.get_frame_duration, None, self.get_frame_duration_async, self.increase_error_count, log_exception=True)

        self.voltage_timer.start()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED,
                                         self.qtcb_frame_rendered.emit)

    def stop(self):
        self.voltage_timer.stop()
        self.led_strip.register_callback(self.led_strip.CALLBACK_FRAME_RENDERED, None)

        if self.has_configurable_rame_rendered_callback and not self.frame_rendered_callback_was_enabled:
            try:
                self.led_strip.disable_frame_rendered_callback()
            except:
                pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLEDStrip.DEVICE_IDENTIFIER
