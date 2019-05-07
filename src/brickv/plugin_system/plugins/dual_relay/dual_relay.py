# -*- coding: utf-8 -*-
"""
Dual Relay Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

dual_relay.py: Dual Relay Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.dual_relay.ui_dual_relay import Ui_DualRelay
from brickv.bindings.bricklet_dual_relay import BrickletDualRelay
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop

class DualRelay(PluginBase, Ui_DualRelay):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletDualRelay, *args)

        self.setupUi(self)

        self.dr = self.device

        self.state1_combobox.setItemData(0, True)
        self.state1_combobox.setItemData(1, False)

        self.state2_combobox.setItemData(0, True)
        self.state2_combobox.setItemData(1, False)

        self.monoflop = Monoflop(self.dr,
                                 [1, 2],
                                 [self.state1_combobox, self.state2_combobox],
                                 self.cb_state_change_by_monoflop,
                                 [self.time1_spinbox, self.time2_spinbox],
                                 None,
                                 self)

        self.dr1_button.clicked.connect(self.dr1_clicked)
        self.dr2_button.clicked.connect(self.dr2_clicked)

        self.go1_button.clicked.connect(self.go1_clicked)
        self.go2_button.clicked.connect(self.go2_clicked)

        self.a1_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_a1.bmp')
        self.a2_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_a2.bmp')
        self.b1_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_b1.bmp')
        self.b2_pixmap = load_masked_pixmap('plugin_system/plugins/dual_relay/relay_b2.bmp')

    def get_state_async(self, dr1, dr2):
        width = self.dr1_button.width()

        if self.dr1_button.minimumWidth() < width:
            self.dr1_button.setMinimumWidth(width)

        width = self.dr2_button.width()

        if self.dr2_button.minimumWidth() < width:
            self.dr2_button.setMinimumWidth(width)

        if dr1:
            self.dr1_button.setText('Switch Off')
            self.dr1_image.setPixmap(self.a1_pixmap)
        else:
            self.dr1_button.setText('Switch On')
            self.dr1_image.setPixmap(self.b1_pixmap)

        if dr2:
            self.dr2_button.setText('Switch Off')
            self.dr2_image.setPixmap(self.a2_pixmap)
        else:
            self.dr2_button.setText('Switch On')
            self.dr2_image.setPixmap(self.b2_pixmap)

    def start(self):
        async_call(self.dr.get_state, None, self.get_state_async, self.increase_error_count,
                   expand_result_tuple_for_callback=True)

        self.monoflop.start()

    def stop(self):
        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualRelay.DEVICE_IDENTIFIER

    def dr1_clicked(self):
        width = self.dr1_button.width()

        if self.dr1_button.minimumWidth() < width:
            self.dr1_button.setMinimumWidth(width)

        state = 'On' in self.dr1_button.text().replace('&', '')

        if state:
            self.dr1_button.setText('Switch Off')
            self.dr1_image.setPixmap(self.a1_pixmap)
        else:
            self.dr1_button.setText('Switch On')
            self.dr1_image.setPixmap(self.b1_pixmap)

        async_call(self.dr.set_selected_state, (1, state), None, self.increase_error_count)

    def dr2_clicked(self):
        width = self.dr2_button.width()

        if self.dr2_button.minimumWidth() < width:
            self.dr2_button.setMinimumWidth(width)

        state = 'On' in self.dr2_button.text().replace('&', '')

        if state:
            self.dr2_button.setText('Switch Off')
            self.dr2_image.setPixmap(self.a2_pixmap)
        else:
            self.dr2_button.setText('Switch On')
            self.dr2_image.setPixmap(self.b2_pixmap)

        async_call(self.dr.set_selected_state, (2, state), None, self.increase_error_count)

    def go1_clicked(self):
        self.monoflop.trigger(1)

    def go2_clicked(self):
        self.monoflop.trigger(2)

    def cb_state_change_by_monoflop(self, relay, state):
        if relay == 1:
            if state:
                self.dr1_button.setText('Switch Off')
                self.dr1_image.setPixmap(self.a1_pixmap)
            else:
                self.dr1_button.setText('Switch On')
                self.dr1_image.setPixmap(self.b1_pixmap)
        elif relay == 2:
            if state:
                self.dr2_button.setText('Switch Off')
                self.dr2_image.setPixmap(self.a2_pixmap)
            else:
                self.dr2_button.setText('Switch On')
                self.dr2_image.setPixmap(self.b2_pixmap)
