# -*- coding: utf-8 -*-
"""
TNG Base Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

tng_base.py: TNG Base Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.tng_base.ui_tng_base import Ui_TNGBase
from brickv.bindings.bricklet_tng_base import BrickletTNGBase
from brickv.async_call import async_call

class TNGBase(COMCUPluginBase, Ui_TNGBase):
    qtcb_high_contrast_image = pyqtSignal(object)
    qtcb_temperature_image = pyqtSignal(object)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletTNGBase, *args)

        self.setupUi(self)
        self.tng_base = self.device

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTNGBase.DEVICE_IDENTIFIER
