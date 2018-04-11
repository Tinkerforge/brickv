# -*- coding: utf-8 -*-
"""
Industrial Digital In 4 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_digital_in_4-v2.py: Industrial Digital In 4 2.0 Plugin Implementation

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

from PyQt4.QtCore import Qt

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

        self.cbe_get_value = CallbackEmulator(self.idi4.get_value,
                                              self.cb_get_value,
                                              self.increase_error_count)

        self.sbox_iv_period.setValue(100)

        self.btn_lc_apply.clicked.connect(self.btn_lc_apply_clicked)
        self.btn_iv_period_apply.clicked.connect(self.btn_iv_period_apply_clicked)

    def start(self):
        self.cbe_get_value.set_period(self.sbox_iv_period.value())

    def stop(self):
        self.cbe_get_value.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalIn4V2.DEVICE_IDENTIFIER

    def cb_get_value(self, value):
        for i, v in enumerate(value):
            if v:
                self.lbl_stat_i_ch[i].setPixmap(self.vcc_pixmap)
                self.lbl_stat_v_ch[i].setText('High')
            else:
                self.lbl_stat_i_ch[i].setPixmap(self.gnd_pixmap)
                self.lbl_stat_v_ch[i].setText('Low')

    def btn_lc_apply_clicked(self):
        self.idi4.set_info_led_config(self.cbox_lc_l.currentIndex(), self.cbox_lc_c.currentIndex())

    def btn_iv_period_apply_clicked(self):
        self.cbe_get_value.set_period(self.sbox_iv_period.value())