# -*- coding: utf-8 -*-
"""
RGB LED Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

rgb_led.py: RGB LED Plugin Implementation

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

from PyQt4.QtCore import  Qt
from PyQt4.QtGui import QLabel, QHBoxLayout, QVBoxLayout, QColorDialog, QColor

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_rgb_led import BrickletRGBLED
from brickv.async_call import async_call

class RGBLED(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRGBLED, *args)

        self.rgb_led = self.device

        self.color_dialog = QColorDialog()
        self.color_dialog.setWindowFlags(Qt.Widget)
        self.color_dialog.setOptions(QColorDialog.DontUseNativeDialog | QColorDialog.NoButtons)
        self.color_dialog.currentColorChanged.connect(self.color_changed)

        layout = QVBoxLayout(self)
        layout.addStretch()

        hlayout = QHBoxLayout()
        hlayout.addStretch()
        hlayout.addWidget(self.color_dialog)
        hlayout.addStretch()

        layout.addLayout(hlayout)
        layout.addStretch()

    def start(self):
        async_call(self.rgb_led.get_rgb_value, None, self.cb_rgb_value, self.increase_error_count)

    def stop(self):
        pass

    def color_changed(self, color):
        r, g, b, _ = color.getRgb()
        self.rgb_led.set_rgb_value(r, g, b)

    def cb_rgb_value(self, rgb):
        color = QColor(rgb.r, rgb.g, rgb.b)
        self.color_dialog.setCurrentColor(color)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rgb_led'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRGBLED.DEVICE_IDENTIFIER
