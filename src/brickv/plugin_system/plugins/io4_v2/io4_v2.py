# -*- coding: utf-8 -*-
"""
IO4 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

humidity.py: IO4 2.0 Plugin Implementation

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

from PyQt5.QtWidgets import QDoubleSpinBox, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.io4_v2.ui_io4_v2 import Ui_IO4V2
from brickv.bindings.bricklet_io4_v2 import BrickletIO4V2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.monoflop import Monoflop

class IO4V2(COMCUPluginBase, Ui_IO4V2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIO4V2, *args)

        self.setupUi(self)

        self.io = self.device

        self.has_monoflop_abort_by_set_configuration = None

        self.io.set_response_expected(self.io.FUNCTION_SET_CONFIGURATION, True)

        self.cbe_value = CallbackEmulator(self,
                                          self.io.get_value,
                                          None,
                                          self.cb_value,
                                          self.increase_error_count)

        self.config_direction = [None] * 4
        self.config_value = [None] * 4

        self.lbl_st_ch_v = [self.lbl_st_ch0_v,
                            self.lbl_st_ch1_v,
                            self.lbl_st_ch2_v,
                            self.lbl_st_ch3_v]

        self.lbl_st_ch_d = [self.lbl_st_ch0_d,
                            self.lbl_st_ch1_d,
                            self.lbl_st_ch2_d,
                            self.lbl_st_ch3_d]

        self.lbl_st_ch_cfg = [self.lbl_st_ch0_cfg,
                              self.lbl_st_ch1_cfg,
                              self.lbl_st_ch2_cfg,
                              self.lbl_st_ch3_cfg]

        self.lbl_st_ch_monoflop_t = [self.lbl_st_ch0_monoflop_t,
                                     self.lbl_st_ch1_monoflop_t,
                                     self.lbl_st_ch2_monoflop_t,
                                     self.lbl_st_ch3_monoflop_t]

        self.cbox_cfg_ch_dir.setItemData(0, self.io.DIRECTION_IN)
        self.cbox_cfg_ch_dir.setItemData(1, self.io.DIRECTION_OUT)

        self.cbox_cfg_ch_v.setItemData(0, True)
        self.cbox_cfg_ch_v.setItemData(1, False)

        self.btn_monoflop_go.clicked.connect(self.btn_monoflop_go_clicked)
        self.btn_cfg_ch_save.clicked.connect(self.btn_cfg_ch_save_clicked)
        self.cbox_cfg_ch.currentIndexChanged.connect(self.cbox_cfg_ch_changed)
        self.cbox_cfg_ch_dir.currentIndexChanged.connect(self.cbox_cfg_ch_dir_changed)

        self.monoflop_values = []
        self.monoflop_times = []

        for i in range(4):
            monoflop_value = QComboBox()
            monoflop_value.addItem('High', 1)
            monoflop_value.addItem('Low', 0)

            self.monoflop_values.append(monoflop_value)
            self.monoflop_value_stack.addWidget(monoflop_value)

            monoflop_time = QDoubleSpinBox()

            self.monoflop_times.append(monoflop_time)
            self.monoflop_time_stack.addWidget(monoflop_time)

        self.monoflop = Monoflop(self.io,
                                 [0, 1, 2, 3],
                                 self.monoflop_values,
                                 self.cb_value_change_by_monoflop,
                                 self.monoflop_times,
                                 self.lbl_st_ch_monoflop_t,
                                 self,
                                 handle_get_monoflop_invalid_parameter_as_abort=True)

    def get_configuration_async(self, channel, direction, value):
        self.config_direction[channel] = direction
        self.config_value[channel] = value

        if direction == self.io.DIRECTION_IN:
            self.lbl_st_ch_d[channel].setText('Input')

            if value:
                self.lbl_st_ch_cfg[channel].setText('Pull-Up')
            else:
                self.lbl_st_ch_cfg[channel].setText('Default')
        else:
            self.lbl_st_ch_d[channel].setText('Output')
            self.lbl_st_ch_cfg[channel].setText('-')

        if None not in self.config_direction: # got all channel data
            self.cbox_cfg_ch_changed(self.cbox_cfg_ch.currentIndex())

    def start(self):
        # the firmware version might change between init and start of a Co-MCU
        # Bricklet plugin, because a Co-MCU Bricklet can be restarted without
        # recreating the plugin. therefore, the firmware version has to be checked
        # on every start
        self.has_monoflop_abort_by_set_configuration = self.firmware_version >= (2, 0, 3)

        self.config_direction = [None] * 4
        self.config_value = [None] * 4

        for channel in range(4):
            async_call(self.io.get_configuration, channel, self.get_configuration_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)

        self.cbe_value.set_period(50)

        self.monoflop.start()

    def stop(self):
        self.cbe_value.set_period(0)

        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIO4V2.DEVICE_IDENTIFIER

    def cb_value(self, value):
        for i in range(4):
            if value[i]:
                self.lbl_st_ch_v[i].setText('High')
            else:
                self.lbl_st_ch_v[i].setText('Low')

    def cb_value_change_by_monoflop(self, channel, value):
        if value:
            self.lbl_st_ch_v[channel].setText('High')
        else:
            self.lbl_st_ch_v[channel].setText('Low')

    def btn_monoflop_go_clicked(self):
        channel = self.cbox_cfg_ch.currentIndex()

        if channel < 0:
            return

        self.monoflop.trigger(channel)

    def set_configuration_async(self, channel, direction, value):
        if not self.has_monoflop_abort_by_set_configuration and direction == self.io.DIRECTION_OUT and self.monoflop.active(channel):
            # the set-configuration function in firmware version < 2.0.3 doesn't
            # abort monoflops, call the set-selected-value that does abort an active monoflop
            async_call(self.io.set_selected_value, (channel, value), None, self.increase_error_count)

    def btn_cfg_ch_save_clicked(self):
        channel = self.cbox_cfg_ch.currentIndex()
        direction = self.cbox_cfg_ch_dir.currentData()
        value = self.cbox_cfg_ch_v.currentData()

        if channel < 0 or direction == None or value == None:
            return

        async_call(self.io.set_configuration, (channel, direction, value), self.set_configuration_async, self.increase_error_count,
                   pass_arguments_to_result_callback=True, expand_arguments_tuple_for_callback=True)
        async_call(self.io.get_configuration, channel, self.get_configuration_async, self.increase_error_count,
                   pass_arguments_to_result_callback=True, expand_result_tuple_for_callback=True)

    def cbox_cfg_ch_changed(self, channel):
        if channel < 0:
            return

        direction = self.config_direction[channel]
        direction_index = self.cbox_cfg_ch_dir.findData(direction)

        self.cbox_cfg_ch_dir.setCurrentIndex(direction_index)
        self.cbox_cfg_ch_dir_changed(direction_index)

        value = self.config_value[channel]
        value_index = self.cbox_cfg_ch_v.findData(value)

        self.cbox_cfg_ch_v.setCurrentIndex(value_index)

        self.monoflop_time_stack.setCurrentIndex(channel)
        self.monoflop_value_stack.setCurrentIndex(channel)

        self.btn_monoflop_go.setEnabled(direction == self.io.DIRECTION_OUT)

    def cbox_cfg_ch_dir_changed(self, index):
        channel = self.cbox_cfg_ch.currentIndex()
        direction = self.cbox_cfg_ch_dir.currentData()

        if channel < 0 or direction == None:
            return

        self.cbox_cfg_ch_v.clear()

        if direction == self.io.DIRECTION_IN:
            self.lbl_cfg_ch_v.setText('Configuration:')
            self.cbox_cfg_ch_v.addItem('Pull-Up', True)
            self.cbox_cfg_ch_v.addItem('Default', False)
        else:
            self.lbl_cfg_ch_v.setText('Value:')
            self.cbox_cfg_ch_v.addItem('High', True)
            self.cbox_cfg_ch_v.addItem('Low', False)

        value = self.config_value[channel]
        value_index = self.cbox_cfg_ch_v.findData(value)

        self.cbox_cfg_ch_v.setCurrentIndex(value_index)
