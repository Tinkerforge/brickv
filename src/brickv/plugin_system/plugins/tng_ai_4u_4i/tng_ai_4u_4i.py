# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

tng_ai_4u_4i.py: TNG AI4U4I Plugin Implementation

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
from brickv.plugin_system.plugins.tng_ai_4u_4i.ui_tng_ai_4u_4i import Ui_TNGAI4U4I
from brickv.bindings.tng_ai_4u_4i import TNGAI4U4I as TNGAI4U4IBindings
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class TNGAI4U4I(TNGPluginBase, Ui_TNGAI4U4I):
    def __init__(self, *args):
        TNGPluginBase.__init__(self, TNGAI4U4IBindings, *args)

        self.setupUi(self)
        self.ai_4u_4i = self.device

        self.voltages = [
            self.label_voltage_ch0,
            self.label_voltage_ch1,
            self.label_voltage_ch2,
            self.label_voltage_ch3,
        ]

        self.currents = [
            self.label_current_ch0,
            self.label_current_ch1,
            self.label_current_ch2,
            self.label_current_ch3,
        ]

        self.cbe_values = CallbackEmulator(self.ai_4u_4i.get_values, None, self.cb_values, self.increase_error_count)

    def cb_values(self, values):
        for i, v in enumerate(values.voltages):
            self.voltages[i].setText('{}mV'.format(v))

        for i, c in enumerate(values.currents):
            self.currents[i].setText('{}uA'.format(c))

    def start(self):
        self.cbe_values.set_period(50)

    def stop(self):
        self.cbe_values.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == TNGAI4U4IBindings.DEVICE_IDENTIFIER
