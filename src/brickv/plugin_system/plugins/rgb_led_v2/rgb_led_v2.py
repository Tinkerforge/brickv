# -*- coding: utf-8 -*-
"""
RGB LED 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

rgb_led_v2.py: RGB LED 2.0 Plugin Implementation

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

from PyQt5.QtCore import  Qt
from PyQt5.QtWidgets import QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtGui import QColor, QPixmap, QIcon, QPainter

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_rgb_led_v2 import BrickletRGBLEDV2
from brickv.plugin_system.plugins.rgb_led_v2.ui_rgb_led_v2 import Ui_RGBLEDV2
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.async_call import async_call

class RGBLEDV2(COMCUPluginBase, Ui_RGBLEDV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRGBLEDV2, *args)

        self.rgb_led = self.device

        self.changing = False
        self.set_rgb_value_response_expected = None

        self.setupUi(self)

        self.r_syncer = SliderSpinSyncer(self.slider_r, self.spin_r, self.rgb_changed, spin_signal='valueChanged')
        self.g_syncer = SliderSpinSyncer(self.slider_g, self.spin_g, self.rgb_changed, spin_signal='valueChanged')
        self.b_syncer = SliderSpinSyncer(self.slider_b, self.spin_b, self.rgb_changed, spin_signal='valueChanged')

        self.h_syncer = SliderSpinSyncer(self.slider_h, self.spin_h, self.hsl_changed, spin_signal='valueChanged')
        self.s_syncer = SliderSpinSyncer(self.slider_s, self.spin_s, self.hsl_changed, spin_signal='valueChanged')
        self.l_syncer = SliderSpinSyncer(self.slider_l, self.spin_l, self.hsl_changed, spin_signal='valueChanged')

        def set_color(r, g, b):
            self.changing = True
            self.spin_r.setValue(r)
            self.spin_g.setValue(g)
            self.spin_b.setValue(b)
            self.changing = False
            self.rgb_changed()

        for color, button in zip([(0, 0, 0), (255, 255, 255), (255, 0, 0), (255, 255, 0),
                                  (0, 255, 0), (0, 255, 255), (0, 0, 255), (255, 0, 255)],
                                [self.button_black, self.button_white, self.button_red, self.button_yellow,
                                 self.button_green, self.button_cyan, self.button_blue, self.button_magenta]):
            button.clicked.connect(lambda clicked, c = color: set_color(*c))
            pixmap = QPixmap(16, 16)
            QPainter(pixmap).fillRect(0, 0, 16, 16, QColor(*color))
            button.setIcon(QIcon(pixmap))
            button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)

    def start(self):
        # Use response expected for set_rgb_value function, to make sure that the
        # data queue can't fill up while you move the slider around.
        self.set_rgb_value_response_expected = self.rgb_led.get_response_expected(self.rgb_led.FUNCTION_SET_RGB_VALUE)
        self.rgb_led.set_response_expected(self.rgb_led.FUNCTION_SET_RGB_VALUE, True)

        async_call(self.rgb_led.get_rgb_value, None, self.get_rgb_value_async, self.increase_error_count)

    def stop(self):
        if self.set_rgb_value_response_expected != None:
            self.rgb_led.set_response_expected(self.rgb_led.FUNCTION_SET_RGB_VALUE, self.set_rgb_value_response_expected)

    def rgb_changed(self, *args):
        if self.changing:
            return

        r, g, b = self.spin_r.value(), self.spin_g.value(), self.spin_b.value()
        rgb = QColor(r, g, b)
        h, s, l = rgb.hslHue(), rgb.hslSaturation(), rgb.lightness()

        self.changing = True

        if h != -1: # Qt returns -1 if the color is achromatic (i.e. grey).
            self.spin_h.setValue(h)
        self.spin_s.setValue(s)
        self.spin_l.setValue(l)
        self.changing = False

        self.rgb_led.set_rgb_value(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def hsl_changed(self, *args):
        if self.changing:
            return

        h, s, l = self.spin_h.value(), self.spin_s.value(), self.spin_l.value()
        hsl = QColor()
        hsl.setHsl(h, s, l)
        r, g, b = hsl.red(), hsl.green(), hsl.blue()

        self.changing = True
        self.spin_r.setValue(r)
        self.spin_g.setValue(g)
        self.spin_b.setValue(b)
        self.changing = False

        self.rgb_led.set_rgb_value(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def get_rgb_value_async(self, rgb):
        self.changing = True
        self.spin_r.setValue(rgb.r)
        self.spin_g.setValue(rgb.g)
        self.spin_b.setValue(rgb.b)
        self.changing = False
        self.rgb_changed()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRGBLEDV2.DEVICE_IDENTIFIER
