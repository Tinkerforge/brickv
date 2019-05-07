# -*- coding: utf-8 -*-
"""
Industrial Dual Relay Plugin
Copyright (C) 2017-2018 Olaf Lüke <olaf@tinkerforge.com>

industrial_dual_relay.py: Industrial Dual Relay Plugin Implementation

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
from brickv.plugin_system.plugins.industrial_dual_relay.ui_industrial_dual_relay import Ui_IndustrialDualRelay
from brickv.bindings.bricklet_industrial_dual_relay import BrickletIndustrialDualRelay
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop

class IndustrialDualRelay(COMCUPluginBase, Ui_IndustrialDualRelay):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDualRelay, *args)

        self.setupUi(self)

        self.idr = self.device

        self.value0_combobox.setItemData(0, True)
        self.value0_combobox.setItemData(1, False)

        self.value1_combobox.setItemData(0, True)
        self.value1_combobox.setItemData(1, False)

        self.monoflop = Monoflop(self.idr,
                                 [0, 1],
                                 [self.value0_combobox, self.value1_combobox],
                                 self.cb_value_change_by_monoflop,
                                 [self.time0_spinbox, self.time1_spinbox],
                                 None,
                                 self)

        self.ch0_button.clicked.connect(self.ch0_clicked)
        self.ch1_button.clicked.connect(self.ch1_clicked)

        self.go0_button.clicked.connect(self.go0_clicked)
        self.go1_button.clicked.connect(self.go1_clicked)

        self.a0_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel0_a.bmp')
        self.a1_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel1_a.bmp')
        self.b0_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel0_b.bmp')
        self.b1_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_dual_relay/channel1_b.bmp')

    def get_value_async(self, value):
        width = self.ch0_button.width()

        if self.ch0_button.minimumWidth() < width:
            self.ch0_button.setMinimumWidth(width)

        width = self.ch1_button.width()

        if self.ch1_button.minimumWidth() < width:
            self.ch1_button.setMinimumWidth(width)

        ch0, ch1 = value

        if ch0:
            self.ch0_button.setText('Switch Off')
            self.ch0_image.setPixmap(self.a0_pixmap)
        else:
            self.ch0_button.setText('Switch On')
            self.ch0_image.setPixmap(self.b0_pixmap)

        if ch1:
            self.ch1_button.setText('Switch Off')
            self.ch1_image.setPixmap(self.a1_pixmap)
        else:
            self.ch1_button.setText('Switch On')
            self.ch1_image.setPixmap(self.b1_pixmap)

    def start(self):
        async_call(self.idr.get_value, None, self.get_value_async, self.increase_error_count)

        self.monoflop.start()

    def stop(self):
        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDualRelay.DEVICE_IDENTIFIER

    def ch0_clicked(self):
        width = self.ch0_button.width()

        if self.ch0_button.minimumWidth() < width:
            self.ch0_button.setMinimumWidth(width)

        value = 'On' in self.ch0_button.text().replace('&', '')

        if value:
            self.ch0_button.setText('Switch Off')
            self.ch0_image.setPixmap(self.a0_pixmap)
        else:
            self.ch0_button.setText('Switch On')
            self.ch0_image.setPixmap(self.b0_pixmap)

        async_call(self.idr.set_selected_value, (0, value), None, self.increase_error_count)

    def ch1_clicked(self):
        width = self.ch1_button.width()

        if self.ch1_button.minimumWidth() < width:
            self.ch1_button.setMinimumWidth(width)

        value = 'On' in self.ch1_button.text().replace('&', '')

        if value:
            self.ch1_button.setText('Switch Off')
            self.ch1_image.setPixmap(self.a1_pixmap)
        else:
            self.ch1_button.setText('Switch On')
            self.ch1_image.setPixmap(self.b1_pixmap)

        async_call(self.idr.set_selected_value, (1, value), None, self.increase_error_count)

    def go0_clicked(self):
        self.monoflop.trigger(0)

    def go1_clicked(self):
        self.monoflop.trigger(1)

    def cb_value_change_by_monoflop(self, channel, value):
        if channel == 0:
            if value:
                self.ch0_button.setText('Switch Off')
                self.ch0_image.setPixmap(self.a0_pixmap)
            else:
                self.ch0_button.setText('Switch On')
                self.ch0_image.setPixmap(self.b0_pixmap)
        elif channel == 1:
            if value:
                self.ch1_button.setText('Switch Off')
                self.ch1_image.setPixmap(self.a1_pixmap)
            else:
                self.ch1_button.setText('Switch On')
                self.ch1_image.setPixmap(self.b1_pixmap)
