# -*- coding: utf-8 -*-
"""
XMC1400 Breakout Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

xmc1400_breakout.py: XMC1400 Breakout Plugin implementation

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

from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_xmc1400_breakout import BrickletXMC1400Breakout
from brickv.callback_emulator import CallbackEmulator

class XMC1400Breakout(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletXMC1400Breakout, *args)

        self.xmc1400 = self.device

        self.cbe_count = CallbackEmulator(self.xmc1400.get_count,
                                          self.cb_count,
                                          self.increase_error_count)

        self.label_count = QLabel()
        self.label_count.setText('Count: TBD')

        self.label_desc = QLabel()
        self.label_desc.setText("""This is the Brick Viewer plugin for the XMC1400 Breakout Bricklet.
The Bricklet is intended for development of new Bricklets.
You can modify this plugin for your own tests with the Bricklet.

Below you can find the count that is returned by the get_count() example.
If the Bricklet is working it should increase once per second.

""")
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.label_desc)
        layout.addWidget(self.label_count)
        layout.addStretch()

        layout_main = QHBoxLayout(self)
        layout_main.addStretch()
        layout_main.addLayout(layout)
        layout_main.addStretch()

    def start(self):
        self.cbe_count.set_period(100)

    def stop(self):
        self.cbe_count.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletXMC1400Breakout.DEVICE_IDENTIFIER

    def cb_count(self, count):
        self.label_count.setText('Count: {0}'.format(count))
