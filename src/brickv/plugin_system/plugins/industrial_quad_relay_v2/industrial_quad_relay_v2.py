# -*- coding: utf-8 -*-
"""
Industrial Quad Relay 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

industrial_quad_relay_v2.py: Industrial Quad Relay 2.0 Plugin Implementation

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

import functools

from PyQt5.QtWidgets import QSpinBox, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.industrial_quad_relay_v2.ui_industrial_quad_relay_v2 import Ui_IndustrialQuadRelayV2
from brickv.bindings.bricklet_industrial_quad_relay_v2 import BrickletIndustrialQuadRelayV2
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop

class IndustrialQuadRelayV2(COMCUPluginBase, Ui_IndustrialQuadRelayV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialQuadRelayV2, *args)

        self.setupUi(self)

        self.iqr = self.device

        self.open_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_quad_relay/relay_open.bmp')
        self.close_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_quad_relay/relay_close.bmp')

        self.relay_buttons = [self.b0, self.b1, self.b2, self.b3]
        self.relay_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon]
        self.relay_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label]

        for icon in self.relay_button_icons:
            icon.setPixmap(self.open_pixmap)
            icon.show()

        for i in range(len(self.relay_buttons)):
            self.relay_buttons[i].clicked.connect(functools.partial(self.relay_button_clicked, i))

        self.monoflop_values = []
        self.monoflop_times = []

        for i in range(4):
            self.monoflop_channel.setItemData(i, i)

            monoflop_value = QComboBox()
            monoflop_value.addItem('On', True)
            monoflop_value.addItem('Off', False)

            self.monoflop_values.append(monoflop_value)
            self.monoflop_value_stack.addWidget(monoflop_value)

            monoflop_time = QSpinBox()
            monoflop_time.setRange(1, (1 << 31) - 1)
            monoflop_time.setValue(1000)

            self.monoflop_times.append(monoflop_time)
            self.monoflop_time_stack.addWidget(monoflop_time)

        self.monoflop = Monoflop(self.iqr,
                                 [0, 1, 2, 3],
                                 self.monoflop_values,
                                 self.cb_value_change_by_monoflop,
                                 self.monoflop_times,
                                 None,
                                 self)

        self.monoflop_channel.currentIndexChanged.connect(self.monoflop_channel_changed)
        self.monoflop_go.clicked.connect(self.monoflop_go_clicked)

        self.cbox_cs0_cfg.currentIndexChanged.connect(self.cbox_cs0_cfg_changed)
        self.cbox_cs1_cfg.currentIndexChanged.connect(self.cbox_cs1_cfg_changed)
        self.cbox_cs2_cfg.currentIndexChanged.connect(self.cbox_cs2_cfg_changed)
        self.cbox_cs3_cfg.currentIndexChanged.connect(self.cbox_cs3_cfg_changed)

    def get_value_async(self, value):
        for button in range(4):
            if value[button]:
                self.relay_buttons[button].setText('Switch Off')
                self.relay_button_icons[button].setPixmap(self.close_pixmap)
            else:
                self.relay_buttons[button].setText('Switch On')
                self.relay_button_icons[button].setPixmap(self.open_pixmap)

    def get_channel_led_config_async(self, idx, cfg):
        if idx == 0:
            self.cbox_cs0_cfg.setCurrentIndex(cfg)
        elif idx == 1:
            self.cbox_cs1_cfg.setCurrentIndex(cfg)
        elif idx == 2:
            self.cbox_cs2_cfg.setCurrentIndex(cfg)
        elif idx == 3:
            self.cbox_cs3_cfg.setCurrentIndex(cfg)

    def cbox_cs0_cfg_changed(self, idx):
        self.iqr.set_channel_led_config(0, idx)

    def cbox_cs1_cfg_changed(self, idx):
        self.iqr.set_channel_led_config(1, idx)

    def cbox_cs2_cfg_changed(self, idx):
        self.iqr.set_channel_led_config(2, idx)

    def cbox_cs3_cfg_changed(self, idx):
        self.iqr.set_channel_led_config(3, idx)

    def start(self):
        async_call(self.iqr.get_value, None, self.get_value_async, self.increase_error_count)

        for channel in range(4):
            async_call(self.iqr.get_channel_led_config, channel, self.get_channel_led_config_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)

        self.monoflop.start()

    def stop(self):
        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialQuadRelayV2.DEVICE_IDENTIFIER

    def relay_button_clicked(self, button):
        value = 'On' in self.relay_buttons[button].text().replace('&', '')

        if value:
            self.relay_buttons[button].setText('Switch Off')
            self.relay_button_icons[button].setPixmap(self.close_pixmap)
        else:
            self.relay_buttons[button].setText('Switch On')
            self.relay_button_icons[button].setPixmap(self.open_pixmap)

        self.iqr.set_selected_value(button, value)

    def cb_value_change_by_monoflop(self, channel, value):
        if value:
            self.relay_buttons[channel].setText('Switch Off')
            self.relay_button_icons[channel].setPixmap(self.close_pixmap)
        else:
            self.relay_buttons[channel].setText('Switch On')
            self.relay_button_icons[channel].setPixmap(self.open_pixmap)

    def monoflop_channel_changed(self):
        channel = self.monoflop_channel.currentData()

        if channel == None:
            return

        self.monoflop_time_stack.setCurrentIndex(channel)
        self.monoflop_value_stack.setCurrentIndex(channel)

    def monoflop_go_clicked(self):
        channel = self.monoflop_channel.currentData()

        if channel == None:
            return

        self.monoflop.trigger(channel)
