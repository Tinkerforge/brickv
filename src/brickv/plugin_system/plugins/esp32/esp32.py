# -*- coding: utf-8 -*-
"""
ESP32 Plugin
Copyright (C) 2022 Matthias Bolte <matthias@tinkerforge.com>

esp32.py: ESP32 Plugin implementation

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

from PyQt5.QtWidgets import QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.brick_esp32 import BrickESP32

class ESP32(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickESP32, *args)

        QHBoxLayout(self)

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickESP32.DEVICE_IDENTIFIER
