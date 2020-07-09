# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

tng_do8.py: TNG DO8 Plugin Implementation

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

import math

from PyQt5.QtCore import pyqtSignal, Qt, QSize, QPoint, QLineF
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QImage, QPainter, QPen, QColor

from brickv.plugin_system.tng_plugin_base import TNGPluginBase
from brickv.plugin_system.plugins.tng_do8.ui_tng_do8 import Ui_TNGDO8
from brickv.bindings.tng_do8 import TNGDO8 as TNGDO8Bindings
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class TNGDO8(TNGPluginBase, Ui_TNGDO8):
    def __init__(self, *args):
        TNGPluginBase.__init__(self, TNGDO8Bindings, *args)

        self.setupUi(self)
        self.do8 = self.device

        self.checkboxes = [
            self.checkbox_ch0,
            self.checkbox_ch1,
            self.checkbox_ch2,
            self.checkbox_ch3,
            self.checkbox_ch4,
            self.checkbox_ch5,
            self.checkbox_ch6,
            self.checkbox_ch7,
        ]

        for checkbox in self.checkboxes:
            checkbox.toggled.connect(self.checkbox_toggled)
    
    def checkbox_toggled(self, _):
        values = []
        for checkbox in self.checkboxes:
            values.append(checkbox.isChecked())
        
        self.do8.set_values(0, values)
    
    def get_values_async(self, values):
        print(values)

    def start(self):
        async_call(self.do8.get_values, None, self.get_values_async, self.increase_error_count)

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == TNGDO8Bindings.DEVICE_IDENTIFIER
