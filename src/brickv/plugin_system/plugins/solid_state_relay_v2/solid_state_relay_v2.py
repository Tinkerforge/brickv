# -*- coding: utf-8 -*-
"""
Solid State Relay V2 Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

solid_state_relay_v2.py: Solid State Relay 2.0 Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.solid_state_relay_v2.ui_solid_state_relay_v2 import Ui_SolidStateRelayV2
from brickv.bindings.bricklet_solid_state_relay_v2 import BrickletSolidStateRelayV2
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop

class SolidStateRelayV2(COMCUPluginBase, Ui_SolidStateRelayV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletSolidStateRelayV2, *args)

        self.setupUi(self)

        self.ssr = self.device

        self.state_combobox.setItemData(0, True)
        self.state_combobox.setItemData(1, False)

        self.monoflop = Monoflop(self.ssr,
                                 None,
                                 self.state_combobox,
                                 self.cb_state_change_by_monoflop,
                                 self.time_spinbox,
                                 None,
                                 self)

        self.ssr_button.clicked.connect(self.ssr_clicked)
        self.go_button.clicked.connect(self.go_clicked)

        self.a_pixmap = load_masked_pixmap('plugin_system/plugins/solid_state_relay/relay_a.bmp')
        self.b_pixmap = load_masked_pixmap('plugin_system/plugins/solid_state_relay/relay_b.bmp')

    def get_state_async(self, state):
        width = self.ssr_button.width()

        if self.ssr_button.minimumWidth() < width:
            self.ssr_button.setMinimumWidth(width)

        if state:
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)

    def start(self):
        async_call(self.ssr.get_state, None, self.get_state_async, self.increase_error_count)

        self.monoflop.start()

    def stop(self):
        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletSolidStateRelayV2.DEVICE_IDENTIFIER

    def ssr_clicked(self):
        width = self.ssr_button.width()

        if self.ssr_button.minimumWidth() < width:
            self.ssr_button.setMinimumWidth(width)

        state = 'On' in self.ssr_button.text().replace('&', '')

        if state:
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)

        async_call(self.ssr.set_state, state, None, self.increase_error_count)

    def go_clicked(self):
        self.monoflop.trigger()

    def cb_state_change_by_monoflop(self, state):
        if state:
            self.ssr_button.setText('Switch Off')
            self.ssr_image.setPixmap(self.a_pixmap)
        else:
            self.ssr_button.setText('Switch On')
            self.ssr_image.setPixmap(self.b_pixmap)
