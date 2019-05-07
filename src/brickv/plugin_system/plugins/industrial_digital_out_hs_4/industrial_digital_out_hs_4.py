# -*- coding: utf-8 -*-
"""
Industrial Digital Out HS 4 Plugin
Copyright (C) 2019 Olaf Lüke <ishraq@tinkerforge.com>

industrial_digital_out_hs_4.py: Industrial Digital Out HS 4 Plugin Implementation

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
from brickv.plugin_system.plugins.industrial_digital_out_hs_4.ui_industrial_digital_out_hs_4 import Ui_IndustrialDigitalOutHS4
from brickv.bindings.bricklet_industrial_digital_out_hs_4 import BrickletIndustrialDigitalOutHS4
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.load_pixmap import load_masked_pixmap
from brickv.monoflop import Monoflop

class IndustrialDigitalOutHS4(COMCUPluginBase, Ui_IndustrialDigitalOutHS4):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialDigitalOutHS4, *args)

        self.setupUi(self)

        self.ido4 = self.device

        self.pixmap_low = load_masked_pixmap('plugin_system/plugins/industrial_digital_out_hs_4/ido4_low.bmp')
        self.pixmap_high = load_masked_pixmap('plugin_system/plugins/industrial_digital_out_hs_4/ido4_high.bmp')

        self.btn_v_c = [self.btn_v_c0, self.btn_v_c1, self.btn_v_c2, self.btn_v_c3]
        self.lbl_s_i_c = [self.lbl_s_i_c0, self.lbl_s_i_c1, self.lbl_s_i_c2, self.lbl_s_i_c3]
        self.cbox_clc_c = [self.cbox_clc_c0, self.cbox_clc_c1, self.cbox_clc_c2, self.cbox_clc_c3]

        self.lbl_vol = [self.lbl_vol0, self.lbl_vol1, self.lbl_vol2, self.lbl_vol3]
        self.lbl_cur = [self.lbl_cur0, self.lbl_cur1, self.lbl_cur2, self.lbl_cur3]

        # Set initial channel status icon
        for lbl in self.lbl_s_i_c:
            lbl.setPixmap(self.pixmap_low)

        # Register value toggle button slots
        for c, b in enumerate(self.btn_v_c):
            b.clicked.connect(functools.partial(self.btn_v_c_clicked, c))

        # Monoflop
        self.cbox_m_c.currentIndexChanged.connect(self.cbox_m_c_changed)
        self.btn_m_go.clicked.connect(self.btn_m_go_clicked)

        self.monoflop_values = []
        self.monoflop_times = []

        for i in range(4):
            self.cbox_m_c.setItemData(i, i)

            monoflop_value = QComboBox()
            monoflop_value.addItem('High', True)
            monoflop_value.addItem('Low', False)

            self.monoflop_values.append(monoflop_value)
            self.monoflop_value_stack.addWidget(monoflop_value)

            monoflop_time = QSpinBox()
            monoflop_time.setRange(1, (1 << 31) - 1)
            monoflop_time.setValue(1000)

            self.monoflop_times.append(monoflop_time)
            self.monoflop_time_stack.addWidget(monoflop_time)

        self.monoflop = Monoflop(self.ido4,
                                 [0, 1, 2, 3],
                                 self.monoflop_values,
                                 self.cb_value_change_by_monoflop,
                                 self.monoflop_times,
                                 None,
                                 self)

        # Channel status LED config
        self.cbox_clc_c0.currentIndexChanged.connect(self.cbox_clc_c0_changed)
        self.cbox_clc_c1.currentIndexChanged.connect(self.cbox_clc_c1_changed)
        self.cbox_clc_c2.currentIndexChanged.connect(self.cbox_clc_c2_changed)
        self.cbox_clc_c3.currentIndexChanged.connect(self.cbox_clc_c3_changed)

        # Measurements
        self.cbe_measurements = CallbackEmulator(self.ido4.get_measurements,
                                                 None,
                                                 self.cb_measurements,
                                                 self.increase_error_count)

    def cb_measurements(self, measurements):
        self.lbl_vol[0].setText('{0:.2f} V'.format(measurements.voltage[0] / 1000.0))
        self.lbl_vol[1].setText('{0:.2f} V'.format(measurements.voltage[0] / 1000.0))
        self.lbl_vol[2].setText('{0:.2f} V'.format(measurements.voltage[1] / 1000.0))
        self.lbl_vol[3].setText('{0:.2f} V'.format(measurements.voltage[1] / 1000.0))

        self.lbl_cur[0].setText('{0} mA'.format(measurements.current[0]))
        self.lbl_cur[1].setText('{0} mA'.format(measurements.current[1]))
        self.lbl_cur[2].setText('{0} mA'.format(measurements.current[2]))
        self.lbl_cur[3].setText('{0} mA'.format(measurements.current[3]))

    def get_value_async(self, value):
        for i, b in enumerate(self.btn_v_c):
            if value[i]:
                b.setText('Set Low')
                self.lbl_s_i_c[i].setPixmap(self.pixmap_high)
            else:
                b.setText('Set High')
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

        self.cbe_measurements.set_period(250)

        self.monoflop.start()

    def stop(self):
        self.cbe_measurements.set_period(0)

        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalOutHS4.DEVICE_IDENTIFIER

    def btn_v_c_clicked(self, channel):
        value = 'High' in self.btn_v_c[channel].text().replace('&', '')

        if value:
            self.btn_v_c[channel].setText('Set Low')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_high)
        else:
            self.btn_v_c[channel].setText('Set High')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_low)

        async_call(self.ido4.set_selected_value, (channel, value), None, self.increase_error_count)

    def cb_value_change_by_monoflop(self, channel, value):
        if value:
            self.btn_v_c[channel].setText('Set Low')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_high)
        else:
            self.btn_v_c[channel].setText('Set High')
            self.lbl_s_i_c[channel].setPixmap(self.pixmap_low)

    def cbox_m_c_changed(self):
        channel = self.cbox_m_c.currentIndex()

        if channel < 0:
            return

        self.monoflop_time_stack.setCurrentIndex(channel)
        self.monoflop_value_stack.setCurrentIndex(channel)

    def btn_m_go_clicked(self):
        channel = self.cbox_m_c.currentIndex()

        if channel < 0:
            return

        self.monoflop.trigger(channel)
