# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2020 Olaf Lüke <olaf@tinkerforge.com>

tng_hub.py: TNG HUB Plugin Implementation

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
from brickv.plugin_system.plugins.tng_hub.ui_tng_hub import Ui_TNGHUB
from brickv.bindings.tng_hub import TNGHUB as TNGHUBBindings
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class TNGHUB(TNGPluginBase, Ui_TNGHUB):
    def __init__(self, *args):
        TNGPluginBase.__init__(self, TNGHUBBindings, *args)

        self.setupUi(self)
        self.hub = self.device


        self.label.setText('Hello, i am TNG-HUB')

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == TNGHUBBindings.DEVICE_IDENTIFIER
