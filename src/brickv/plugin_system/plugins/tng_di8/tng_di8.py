# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

tng_di8.py: TNG DI8 Plugin Implementation

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
from brickv.plugin_system.plugins.tng_di8.ui_tng_di8 import Ui_TNGDI8
from brickv.bindings.tng_di8 import TNGDI8 as TNGDI8Bindings
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class TNGDI8(TNGPluginBase, Ui_TNGDI8):
    def __init__(self, *args):
        TNGPluginBase.__init__(self, TNGDI8Bindings, *args)

        self.setupUi(self)
        self.di8 = self.device

        self.cbe_value = CallbackEmulator(self.di8.get_value, None, self.cb_value, self.increase_error_count)

    def cb_value(self, value):
        s = ''
        for x in value:
            if x:
                s += '1'
            else:
                s += '0'
        self.label.setText(s)

    def start(self):
        self.cbe_value.set_period(50)

    def stop(self):
        self.cbe_value.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == TNGDI8Bindings.DEVICE_IDENTIFIER
