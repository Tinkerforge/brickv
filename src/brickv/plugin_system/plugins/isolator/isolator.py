# -*- coding: utf-8 -*-
"""
Isolator Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

isolator.py: Isolator Plugin Implementation

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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QCheckBox, QLabel

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_isolator import BrickletIsolator
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class Isolator(COMCUPluginBase):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIsolator, *args)

        self.isolator = self.device

        self.label = QLabel(u'Isolator Bricklet')

        layout_main = QVBoxLayout(self)
        layout_main.addWidget(self.label)

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIsolator.DEVICE_IDENTIFIER