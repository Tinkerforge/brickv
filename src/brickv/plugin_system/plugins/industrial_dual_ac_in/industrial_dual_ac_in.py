# -*- coding: utf-8 -*-
"""
Industrial Dual AC In Plugin
Copyright (C) 2023 Olaf Lüke <olaf@tinkerforge.com>

industrial_dual_ac_in.py: Industrial Dual AC In Plugin Implementation

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
from brickv.plugin_system.plugins.industrial_dual_ac_in.ui_industrial_dual_ac_in import Ui_IndustrialDualACIn
from brickv.bindings.bricklet_industrial_dual_ac_in import BrickletIndustrialDualACIn
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.load_pixmap import load_masked_pixmap

class IndustrialDualACIn(COMCUPluginBase, Ui_IndustrialDualACIn):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDualACIn, *args)

        self.setupUi(self)

        self.ac_in = self.device

        self.lbl_stat_v_ch = [self.lbl_stat_v_ch0, self.lbl_stat_v_ch1]

        self.cbe_get_value = CallbackEmulator(self,
                                              self.ac_in.get_value,
                                              None,
                                              self.cb_value,
                                              self.increase_error_count)

        self.cbox_cs0_cfg.currentIndexChanged.connect(self.cbox_cs0_cfg_changed)
        self.cbox_cs1_cfg.currentIndexChanged.connect(self.cbox_cs1_cfg_changed)

    def start(self):
        for channel in range(2):
            async_call(self.ac_in.get_channel_led_config, channel, self.get_channel_led_config_async, self.increase_error_count, pass_arguments_to_result_callback=True)

        self.cbe_get_value.set_period(100)

    def stop(self):
        self.cbe_get_value.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDualACIn.DEVICE_IDENTIFIER

    def cb_value(self, value):
        for i, v in enumerate(value):
            if v:
                self.lbl_stat_v_ch[i].setText('AC voltage is present')
            else:
                self.lbl_stat_v_ch[i].setText('-')

    def get_channel_led_config_async(self, idx, cfg):
        if idx == 0:
            self.cbox_cs0_cfg.setCurrentIndex(cfg)
        elif idx == 1:
            self.cbox_cs1_cfg.setCurrentIndex(cfg)

    def cbox_cs0_cfg_changed(self, idx):
        self.ac_in.set_channel_led_config(0, idx)

    def cbox_cs1_cfg_changed(self, idx):
        self.ac_in.set_channel_led_config(1, idx)