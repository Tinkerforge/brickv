# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

tng_ao_4u_4i.py: TNG AO4U4I Plugin Implementation

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
from brickv.plugin_system.plugins.tng_ao_4u_4i.ui_tng_ao_4u_4i import Ui_TNGAO4U4I
from brickv.bindings.tng_ao_4u_4i import TNGAO4U4I as TNGAO4U4IBindings
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.slider_spin_syncer import SliderSpinSyncer

class TNGAO4U4I(TNGPluginBase, Ui_TNGAO4U4I):
    def __init__(self, *args):
        TNGPluginBase.__init__(self, TNGAO4U4IBindings, *args)

        self.setupUi(self)
        self.ao_4u_4i = self.device

        self.voltages = [
            SliderSpinSyncer(self.slider_voltage_ch0, self.spin_voltage_ch0, self.value_changed),
            SliderSpinSyncer(self.slider_voltage_ch1, self.spin_voltage_ch1, self.value_changed),
            SliderSpinSyncer(self.slider_voltage_ch2, self.spin_voltage_ch2, self.value_changed),
            SliderSpinSyncer(self.slider_voltage_ch3, self.spin_voltage_ch3, self.value_changed)
        ]

        self.currents = [
            SliderSpinSyncer(self.slider_current_ch0, self.spin_current_ch0, self.value_changed),
            SliderSpinSyncer(self.slider_current_ch1, self.spin_current_ch1, self.value_changed),
            SliderSpinSyncer(self.slider_current_ch2, self.spin_current_ch2, self.value_changed),
            SliderSpinSyncer(self.slider_current_ch3, self.spin_current_ch3, self.value_changed)
        ]

    def value_changed(self, _):
        v = []
        c = []
        for i in range(4):
            v.append(self.voltages[i].slider.value())
            c.append(self.currents[i].slider.value())
        
        self.ao_4u_4i.set_values(0, v, c)
        print(v, c)

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == TNGAO4U4IBindings.DEVICE_IDENTIFIER
