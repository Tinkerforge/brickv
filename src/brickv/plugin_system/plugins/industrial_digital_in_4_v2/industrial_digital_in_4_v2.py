# -*- coding: utf-8 -*-
"""
Industrial Digital In 4 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_digital_in_4_v2.py: Industrial Digital In 4 2.0 Plugin Implementation

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
from brickv.plugin_system.plugins.industrial_digital_in_4_v2.ui_industrial_digital_in_4_v2 import Ui_IndustrialDigitalIn4V2
from brickv.bindings.bricklet_industrial_digital_in_4_v2 import BrickletIndustrialDigitalIn4V2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.load_pixmap import load_masked_pixmap

class IndustrialDigitalIn4V2(COMCUPluginBase, Ui_IndustrialDigitalIn4V2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDigitalIn4V2, *args)

        self.setupUi(self)

        self.idi4 = self.device

        self.gnd_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_digital_in_4/dio_gnd.bmp')
        self.vcc_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_digital_in_4/dio_vcc.bmp')

        self.lbl_stat_i_ch = [self.lbl_stat_i_ch0, self.lbl_stat_i_ch1, self.lbl_stat_i_ch2, self.lbl_stat_i_ch3]
        self.lbl_stat_v_ch = [self.lbl_stat_v_ch0, self.lbl_stat_v_ch1, self.lbl_stat_v_ch2, self.lbl_stat_v_ch3]

        self.cbe_get_value = CallbackEmulator(self,
                                              self.idi4.get_value,
                                              None,
                                              self.cb_value,
                                              self.increase_error_count)

        self.cbox_cs0_cfg.currentIndexChanged.connect(self.cbox_cs0_cfg_changed)
        self.cbox_cs1_cfg.currentIndexChanged.connect(self.cbox_cs1_cfg_changed)
        self.cbox_cs2_cfg.currentIndexChanged.connect(self.cbox_cs2_cfg_changed)
        self.cbox_cs3_cfg.currentIndexChanged.connect(self.cbox_cs3_cfg_changed)

    def start(self):
        for channel in range(4):
            async_call(self.idi4.get_channel_led_config, channel, self.get_channel_led_config_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)

        self.cbe_get_value.set_period(100)

    def stop(self):
        self.cbe_get_value.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalIn4V2.DEVICE_IDENTIFIER

    def cb_value(self, value):
        for i, v in enumerate(value):
            if v:
                self.lbl_stat_i_ch[i].setPixmap(self.vcc_pixmap)
                self.lbl_stat_v_ch[i].setText('High')
            else:
                self.lbl_stat_i_ch[i].setPixmap(self.gnd_pixmap)
                self.lbl_stat_v_ch[i].setText('Low')

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
        self.idi4.set_channel_led_config(0, idx)

    def cbox_cs1_cfg_changed(self, idx):
        self.idi4.set_channel_led_config(1, idx)

    def cbox_cs2_cfg_changed(self, idx):
        self.idi4.set_channel_led_config(2, idx)

    def cbox_cs3_cfg_changed(self, idx):
        self.idi4.set_channel_led_config(3, idx)
