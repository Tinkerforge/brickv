# -*- coding: utf-8 -*-
"""
Industrial Digital Out 4 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_digital_out_4_v2.py: Industrial Digital Out 4 2.0 Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.industrial_digital_out_4_v2.ui_industrial_digital_out_4_v2 import Ui_IndustrialDigitalOut4V2
from brickv.bindings.bricklet_industrial_digital_out_4_v2 import BrickletIndustrialDigitalOut4V2
from brickv.async_call import async_call
from brickv.load_pixmap import load_masked_pixmap

class IndustrialDigitalOut4V2(COMCUPluginBase, Ui_IndustrialDigitalOut4V2):
    qtcb_monoflop = pyqtSignal(int, int)

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDigitalOut4V2, *args)

        self.setupUi(self)

        self.ido4 = self.device

        self.pixmap_low = load_masked_pixmap('plugin_system/plugins/industrial_digital_out_4_v2/ido4_low.bmp')
        self.pixmap_high = load_masked_pixmap('plugin_system/plugins/industrial_digital_out_4_v2/ido4_high.bmp')

        self.btn_v_c = [
            {
                'btn': self.btn_v_c0,
                'state': False
            },
            {
                'btn': self.btn_v_c1,
                'state': False
            },
            {
                'btn': self.btn_v_c2,
                'state': False
            },
            {
                'btn': self.btn_v_c3,
                'state': False
            }
        ]

        self.lbl_s_i_c = [self.lbl_s_i_c0, self.lbl_s_i_c1, self.lbl_s_i_c2, self.lbl_s_i_c3]
        self.cbox_clc_c = [self.cbox_clc_c0, self.cbox_clc_c1, self.cbox_clc_c2, self.cbox_clc_c3]

        # Set initial channel status icon
        for lbl in self.lbl_s_i_c:
            lbl.setPixmap(self.pixmap_low)

        def get_button_lambda(channel):
            return lambda: self.btn_v_c_clicked(channel)

        # Register value toggle button slots
        for c, b in enumerate(self.btn_v_c):
            b['btn'].clicked.connect(get_button_lambda(c))

        # Monoflop
        self.qtcb_monoflop.connect(self.cb_monoflop_done)
        self.ido4.register_callback(self.ido4.CALLBACK_MONOFLOP_DONE,
                                    self.qtcb_monoflop.emit)

        self.cbox_m_c.currentIndexChanged.connect(self.cbox_m_c_changed)
        self.btn_m_go.clicked.connect(self.btn_m_go_clicked)
        self.monoflop_time_before = [1000] * 4
        self.monoflop_pending = [False] * 4

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        # Channel status LED config
        self.cbox_clc_c0.currentIndexChanged.connect(self.cbox_clc_c0_changed)
        self.cbox_clc_c1.currentIndexChanged.connect(self.cbox_clc_c1_changed)
        self.cbox_clc_c2.currentIndexChanged.connect(self.cbox_clc_c2_changed)
        self.cbox_clc_c3.currentIndexChanged.connect(self.cbox_clc_c3_changed)

    def get_value_async(self, value):
        for i, b in enumerate(self.btn_v_c):
            if value[i]:
                b['btn'].setText('Set Low')
                self.lbl_s_i_c[i].setPixmap(self.pixmap_high)
            else:
                b['btn'].setText('Set High')
                self.lbl_s_i_c[i].setPixmap(self.pixmap_low)

    def get_channel_led_config_async(self, channel, config):
        if channel == 0:
            self.cbox_clc_c0.setCurrentIndex(config)
        elif channel == 1:
            self.cbox_clc_c1.setCurrentIndex(config)
        elif channel == 2:
            self.cbox_clc_c2.setCurrentIndex(config)
        elif channel == 3:
            self.cbox_clc_c3.setCurrentIndex(config)

    def cbox_clc_c0_changed(self, config):
        self.ido4.set_channel_led_config(0, config)

    def cbox_clc_c1_changed(self, config):
        self.ido4.set_channel_led_config(1, config)

    def cbox_clc_c2_changed(self, config):
        self.ido4.set_channel_led_config(2, config)

    def cbox_clc_c3_changed(self, config):
        self.ido4.set_channel_led_config(3, config)

    def start(self):
        async_call(self.ido4.get_value, None, self.get_value_async, self.increase_error_count)

        for channel in range(4):
            async_call(self.ido4.get_channel_led_config, channel, self.get_channel_led_config_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalOut4V2.DEVICE_IDENTIFIER

    def btn_v_c_clicked(self, channel):
        if self.btn_v_c[channel]['state']:
            self.btn_v_c[channel]['state'] = False
            self.btn_v_c[channel]['btn'].setText('Set High')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_low)
        else:
            self.btn_v_c[channel]['state'] = True
            self.btn_v_c[channel]['btn'].setText('Set Low')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_high)

        self.ido4.set_selected_value(channel, self.btn_v_c[channel]['state'])

        self.update_timer.stop()

        for c in range(4):
            self.monoflop_pending[c] = False

        channel = self.cbox_m_c.currentIndex()

        self.sbox_m_t.setValue(self.monoflop_time_before[channel])
        self.sbox_m_t.setEnabled(True)

    def cb_monoflop_done(self, channel, value):
        self.monoflop_pending[channel] = False

        if value:
            self.btn_v_c[channel]['btn'].setText('Set Low')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_high)
        else:
            self.btn_v_c[channel]['btn'].setText('Set High')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_low)

        if sum(self.monoflop_pending) == 0:
            self.update_timer.stop()

        current_channel = self.cbox_m_c.currentIndex()

        if current_channel == channel:
            self.sbox_m_t.setValue(self.monoflop_time_before[current_channel])
            self.sbox_m_t.setEnabled(True)

    def cbox_m_c_changed(self):
        try:
            channel = self.cbox_m_c.currentIndex()
        except ValueError:
            return

        if self.monoflop_pending[channel]:
            async_call(self.ido4.get_monoflop, channel, self.get_monoflop_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)
            self.sbox_m_t.setEnabled(False)
        else:
            self.sbox_m_t.setValue(self.monoflop_time_before[channel])
            self.sbox_m_t.setEnabled(True)

    def btn_m_go_clicked(self):
        channel = self.cbox_m_c.currentIndex()

        if self.monoflop_pending[channel]:
            time = self.monoflop_time_before[channel]
        else:
            time = self.sbox_m_t.value()

        value = self.cbox_m_v.currentIndex() == 1

        self.sbox_m_t.setEnabled(False)
        self.monoflop_time_before[channel] = time
        self.monoflop_pending[channel] = True

        self.ido4.set_monoflop(channel, value, time)

        if value:
            self.btn_v_c[channel]['btn'].setText('Set Low')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_high)
        else:
            self.btn_v_c[channel]['btn'].setText('Set High')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_low)

        self.update_timer.start()

    def get_monoflop_async(self, channel, _state, _time, time_remaining):
        if self.monoflop_pending[channel]:
            self.sbox_m_t.setValue(time_remaining)

    def update(self):
        try:
            channel = self.cbox_m_c.currentIndex()
        except ValueError:
            return

        async_call(self.ido4.get_monoflop, channel, self.get_monoflop_async, self.increase_error_count,
                   pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)
