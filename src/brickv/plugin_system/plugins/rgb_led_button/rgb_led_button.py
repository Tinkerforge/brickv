# -*- coding: utf-8 -*-
"""
RGB LED Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

rgb_led_button.py: RGB LED Button Plugin Implementation

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

from PyQt5.QtGui import QColor

from PyQt5.QtCore import pyqtSignal
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_rgb_led_button import BrickletRGBLEDButton
from brickv.plugin_system.plugins.rgb_led_button.ui_rgb_led_button import Ui_RGBLEDButton
from brickv.slider_spin_syncer import SliderSpinSyncer
from brickv.async_call import async_call

class RGBLEDButton(COMCUPluginBase, Ui_RGBLEDButton):
    qtcb_button_state_changed = pyqtSignal(int)
    
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRGBLEDButton, *args)

        self.rgb_led_button = self.device

        self.changing = False

        self.setupUi(self)
        
        self.qtcb_button_state_changed.connect(self.cb_button_state_changed)
        self.rgb_led_button.register_callback(self.rgb_led_button.CALLBACK_BUTTON_STATE_CHANGED,
                                              self.qtcb_button_state_changed.emit)

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

        self.button_black.clicked.connect(lambda: set_color(0, 0, 0))
        self.button_white.clicked.connect(lambda: set_color(255, 255, 255))
        self.button_red.clicked.connect(lambda: set_color(255, 0, 0))
        self.button_yellow.clicked.connect(lambda: set_color(255, 255, 0))
        self.button_green.clicked.connect(lambda: set_color(0, 255, 0))
        self.button_cyan.clicked.connect(lambda: set_color(0, 255, 255))
        self.button_blue.clicked.connect(lambda: set_color(0, 0, 255))
        self.button_magenta.clicked.connect(lambda: set_color(255, 0, 255))

    def start(self):
        async_call(self.rgb_led_button.get_color, None, self.get_color_async, self.increase_error_count)
        async_call(self.rgb_led_button.get_button_state, None, self.cb_button_state_changed, self.increase_error_count)

    def stop(self):
        pass
    
    def cb_button_state_changed(self, state):
        if state == self.rgb_led_button.BUTTON_STATE_RELEASED:
            self.label_button_state.setText('Released')
        else:
            self.label_button_state.setText('Pressed')

    def rgb_changed(self, *args):
        if self.changing:
            return

        r, g, b = self.spin_r.value(), self.spin_g.value(), self.spin_b.value()
        rgb = QColor(r, g, b)
        h, s, l = rgb.hue(), rgb.saturation(), rgb.lightness()

        self.changing = True
        self.spin_h.setValue(h)
        self.spin_s.setValue(s)
        self.spin_l.setValue(l)
        self.changing = False

        self.rgb_led_button.set_color(r, g, b)
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

        self.rgb_led_button.set_color(r, g, b)
        self.label_color.setStyleSheet('QLabel {{ background: #{:02x}{:02x}{:02x} }}'.format(r, g, b))

    def get_color_async(self, rgb):
        self.changing = True
        self.spin_r.setValue(rgb.red)
        self.spin_g.setValue(rgb.green)
        self.spin_b.setValue(rgb.blue)
        self.changing = False
        self.rgb_changed()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRGBLEDButton.DEVICE_IDENTIFIER
