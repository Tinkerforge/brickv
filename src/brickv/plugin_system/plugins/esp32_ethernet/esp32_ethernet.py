# -*- coding: utf-8 -*-
"""
ESP32 Ethernet Plugin
Copyright (C) 2022 Matthias Bolte <matthias@tinkerforge.com>

esp32_ethernet.py: ESP32 Ethernet Plugin implementation

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

from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.brick_esp32_ethernet import BrickESP32Ethernet
from brickv.plugin_system.plugins.esp32_ethernet.ui_esp32_ethernet import Ui_ESP32Ethernet
from brickv.utils import get_main_window

class ESP32Ethernet(PluginBase, Ui_ESP32Ethernet):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickESP32Ethernet, *args)

        self.setupUi(self)

        self.button_open_web_interface.clicked.connect(self.open_web_interface)

    def open_web_interface(self):
        QDesktopServices.openUrl(QUrl('http://{0}'.format(get_main_window().get_last_host())))

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickESP32Ethernet.DEVICE_IDENTIFIER
