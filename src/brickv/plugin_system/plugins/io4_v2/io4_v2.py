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

from PyQt5.QtCore import QTimer

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.io4_v2.ui_io4_v2 import Ui_IO4V2
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_io4_v2 import BrickletIO4V2
from brickv.async_call import async_call

class IO4V2(COMCUPluginBase, Ui_IO4V2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIO4V2, *args)

        self.setupUi(self)

        self.io = self.device

        self.on_focus = False

        self.ch_current_config = {
                                    0: None,
                                    1: None,
                                    2: None,
                                    3: None
                                 }

        self.async_data_store = {
                                    'all_ch_status_update': {
                                        'ch_values': None,
                                        'ch_config': None,
                                        'monoflop': {
                                            0: { 'running': False, 'start_time_remaining': 500 },
                                            1: { 'running': False, 'start_time_remaining': 500 },
                                            2: { 'running': False, 'start_time_remaining': 500 },
                                            3: { 'running': False, 'start_time_remaining': 500 }
                                        }
                                    },
                                    'update_current_channel_info': {
                                        'value': None,
                                        'config': None,
                                    },
                                    'iv_cb': {
                                        'direction': {
                                            0: None,
                                            1: None,
                                            2: None,
                                            3: None
                                        },
                                        'values': None
                                    }
                                }

        self.gui_grp_cfg_ch_in = [self.lbl_cfg_ch_in_v,
                                  self.cbox_cfg_ch_in_v]

        self.gui_grp_cfg_ch_out = [self.lbl_cfg_ch_out_v,
                                   self.cbox_cfg_ch_out_v,
                                   self.lbl_monoflop,
                                   self.cbox_monoflop_v,
                                   self.sbox_monoflop_t,
                                   self.btn_monoflop_go]

        self.gui_grp_monoflop = [self.cbox_monoflop_v,
                                 self.sbox_monoflop_t,
                                 self.btn_monoflop_go]

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

        self.ch_status_update_timer = QTimer(self)
        self.ch_status_update_timer.timeout.connect(self.ch_status_update_timeout)

        self.iv_cb_timer = QTimer(self)
        self.iv_cb_timer.timeout.connect(self.iv_cb_timeout)

        self.btn_monoflop_go.clicked.connect(self.btn_monoflop_go_clicked)
        self.btn_cfg_ch_apply.clicked.connect(self.btn_cfg_ch_apply_clicked)
        self.cbox_cfg_ch.currentIndexChanged.connect(self.cbox_cfg_ch_changed)
        self.cbox_cfg_ch_dir.currentIndexChanged.connect(self.cbox_cfg_ch_dir_changed)

    def start(self):
        self.on_focus = True
        self.cbox_cfg_ch_changed(self.cbox_cfg_ch.currentIndex())
        self.ch_status_update_timeout()
        self.iv_cb_timeout()

    def stop(self):
        self.on_focus = False
        self.ch_status_update_timer.stop()
        self.iv_cb_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIO4V2.DEVICE_IDENTIFIER

    def generator_ch_status_update_timeout(self):
        def async_get_value(value):
            self.async_data_store['all_ch_status_update']['ch_values'] = value
            next(self.gen_ch_status_update_timeout)

        def async_get_configuration(config):
            self.async_data_store['all_ch_status_update']['ch_config'] = config
            next(self.gen_ch_status_update_timeout)

        def async_get_monoflop(channel, monoflop):
            if self.async_data_store['all_ch_status_update']['monoflop'][channel]['running']:
                if monoflop.time_remaining > 0:
                    if self.cbox_cfg_ch.currentIndex() == channel:
                        for e in self.gui_grp_monoflop:
                            e.setEnabled(False)

                        self.sbox_monoflop_t.setValue(monoflop.time_remaining)

                    self.lbl_st_ch_monoflop_t[channel].setText(str(monoflop.time_remaining))
                else:
                    if self.cbox_cfg_ch.currentIndex() == channel:
                        for e in self.gui_grp_monoflop:
                            e.setEnabled(True)

                        self.sbox_monoflop_t.setValue(self.async_data_store['all_ch_status_update']['monoflop'][channel]['start_time_remaining'])

                    self.async_data_store['all_ch_status_update']['monoflop'][i]['running'] = False
                    self.lbl_st_ch_monoflop_t[channel].setText('0')

            next(self.gen_ch_status_update_timeout)

        async_call(self.io.get_value, None, async_get_value, self.increase_error_count)

        yield

        for i in range(0, 4):
            async_call(self.io.get_configuration,
                       i,
                       async_get_configuration,
                       self.increase_error_count)

            yield

            if self.async_data_store['all_ch_status_update']['ch_config'].direction == self.io.DIRECTION_IN:
                self.lbl_st_ch_d[i].setText('Input')

                if self.async_data_store['all_ch_status_update']['ch_config'].value:
                    self.lbl_st_ch_cfg[i].setText('Pull-Up')
                else:
                    self.lbl_st_ch_cfg[i].setText('Default')

                if self.async_data_store['all_ch_status_update']['ch_values'][i]:
                    self.lbl_st_ch_v[i].setText('High')
                else:
                    self.lbl_st_ch_v[i].setText('Low')
            else:
                self.lbl_st_ch_cfg[i].setText('-')
                self.lbl_st_ch_d[i].setText('Output')

                if self.async_data_store['all_ch_status_update']['ch_values'][i]:
                    self.lbl_st_ch_v[i].setText('High')
                else:
                    self.lbl_st_ch_v[i].setText('Low')

                if self.async_data_store['all_ch_status_update']['monoflop'][i]['running']:
                    async_call(self.io.get_monoflop, i, lambda x: async_get_monoflop(i, x), self.increase_error_count)

                    yield

        self.ch_status_update_timer.start(50)

    def ch_status_update_timeout(self):
        self.ch_status_update_timer.stop()

        if not self.on_focus:
            return

        self.gen_ch_status_update_timeout = self.generator_ch_status_update_timeout()
        next(self.gen_ch_status_update_timeout)

    def generator_iv_cb_timeout(self):
        def async_get_value(value):
            self.async_data_store['iv_cb']['values'] = value
            next(self.gen_iv_cb_timeout)

        def async_get_configuration(channel, config):
            self.async_data_store['iv_cb']['direction'][channel] = config.direction
            next(self.gen_iv_cb_timeout)

        async_call(self.io.get_value, None, async_get_value, self.increase_error_count)

        yield

        for i in range(0, 4):
            async_call(self.io.get_configuration,
                       i,
                       lambda config: async_get_configuration(i, config),
                       self.increase_error_count)

            yield

            if self.async_data_store['iv_cb']['direction'][i] == self.io.DIRECTION_OUT:
                continue

            if self.async_data_store['iv_cb']['values'][i]:
                self.lbl_st_ch_v[i].setText('High')
            else:
                self.lbl_st_ch_v[i].setText('Low')

        self.iv_cb_timer.start(100)

    def iv_cb_timeout(self):
        self.iv_cb_timer.stop()

        if not self.on_focus:
            return

        self.gen_iv_cb_timeout = self.generator_iv_cb_timeout()
        next(self.gen_iv_cb_timeout)

    def btn_monoflop_go_clicked(self):
        channel = self.cbox_cfg_ch.currentIndex()
        monoflop_time = self.sbox_monoflop_t.value()
        direction = self.cbox_cfg_ch_dir.currentIndex()
        monoflop_value = self.cbox_monoflop_v.currentIndex()

        if direction != 1:
            return

        try:
            if monoflop_value == 0:
                value = False
            else:
                value = True

            self.io.set_monoflop(channel, value, monoflop_time)

            self.async_data_store['all_ch_status_update']['monoflop'][channel]['running'] = True
            self.async_data_store['all_ch_status_update']['monoflop'][channel]['start_time_remaining'] = monoflop_time
            self.lbl_st_ch_monoflop_t[channel].setText(str(monoflop_time))

            for e in self.gui_grp_monoflop:
                e.setEnabled(False)
        except ip_connection.Error:
            self.async_data_store['all_ch_status_update']['monoflop'][channel]['running'] = False
            self.async_data_store['all_ch_status_update']['monoflop'][channel]['start_time_remaining'] = 0
            self.lbl_st_ch_monoflop_t[channel].setText('0')

            for e in self.gui_grp_monoflop:
                e.setEnabled(True)

    def btn_cfg_ch_apply_clicked(self):
        self.btn_cfg_ch_apply.setEnabled(False)

        channel = self.cbox_cfg_ch.currentIndex()

        if self.cbox_cfg_ch_dir.currentIndex() == 0:
            try:
                if self.cbox_cfg_ch_in_v.currentIndex() == 0:
                    value = False
                else:
                    value = True

                self.io.set_configuration(channel, self.io.DIRECTION_IN, value)

                self.lbl_st_ch_monoflop_t[channel].setText('0')
                self.async_data_store['all_ch_status_update']['monoflop'][channel]['running'] = False
            except ip_connection.Error:
                return
        else:
            try:
                if self.cbox_cfg_ch_out_v.currentIndex() == 0:
                    value = False
                else:
                    value = True

                self.io.set_configuration(channel, self.io.DIRECTION_OUT, value)
            except ip_connection.Error:
                return

        self.cbox_cfg_ch.setCurrentIndex(channel)
        self.cbox_cfg_ch_changed(channel)
        self.btn_cfg_ch_apply.setEnabled(True)

    def cbox_cfg_ch_changed(self, index):
        self.update_current_channel_info(index)

    def cbox_cfg_ch_dir_changed(self, index):
        if index == 0:
            for e in self.gui_grp_cfg_ch_in:
                e.show()

            for e in self.gui_grp_cfg_ch_out:
                e.hide()
        elif index == 1:
            for e in self.gui_grp_cfg_ch_in:
                e.hide()

            for e in self.gui_grp_cfg_ch_out:
                e.show()

    def update_ch_config_gui(self, index):
        if self.ch_current_config[index]['direction'] == self.io.DIRECTION_IN:
            if self.async_data_store['update_current_channel_info']['config'].value:
                self.cbox_cfg_ch_in_v.setCurrentIndex(1)
            else:
                self.cbox_cfg_ch_in_v.setCurrentIndex(0)

            for e in self.gui_grp_monoflop:
                e.setEnabled(False)

            self.sbox_monoflop_t.setValue(self.async_data_store['all_ch_status_update']['monoflop'][index]['start_time_remaining'])
        else:
            if self.ch_current_config[index]['value']:
                self.cbox_cfg_ch_out_v.setCurrentIndex(1)
            else:
                self.cbox_cfg_ch_out_v.setCurrentIndex(0)

            if self.async_data_store['all_ch_status_update']['monoflop'][index]['running']:
                for e in self.gui_grp_monoflop:
                    e.setEnabled(False)
            else:
                for e in self.gui_grp_monoflop:
                    e.setEnabled(True)

                self.sbox_monoflop_t.setValue(self.async_data_store['all_ch_status_update']['monoflop'][index]['start_time_remaining'])

    def generator_update_current_channel_info(self, ch_index):
        ch_config_d = {
                        'direction': None,
                        'value': None
                      }

        def async_get_configuration(config):
            self.async_data_store['update_current_channel_info']['config'] = config
            next(self.gen_update_current_channel_info)

        def async_get_value(value):
            self.async_data_store['update_current_channel_info']['value'] = value
            next(self.gen_update_current_channel_info)

        async_call(self.io.get_configuration, ch_index, async_get_configuration, self.increase_error_count)

        yield

        async_call(self.io.get_value, None, lambda value: async_get_value(value[ch_index]), self.increase_error_count)

        yield

        if self.async_data_store['update_current_channel_info']['config'].direction == self.io.DIRECTION_IN:
            ch_config_d['direction'] = self.io.DIRECTION_IN
        else:
            ch_config_d['direction'] = self.io.DIRECTION_OUT

        ch_config_d['value'] = self.async_data_store['update_current_channel_info']['value']
        self.ch_current_config[ch_index] = ch_config_d
        self.update_ch_config_gui(ch_index)

        if self.ch_current_config[ch_index]['direction'] == self.io.DIRECTION_IN:
            self.cbox_cfg_ch_dir.setCurrentIndex(0)
            self.cbox_cfg_ch_dir_changed(0)
        else:
            self.cbox_cfg_ch_dir.setCurrentIndex(1)
            self.cbox_cfg_ch_dir_changed(1)

    def update_current_channel_info(self, ch_index):
        self.gen_update_current_channel_info = self.generator_update_current_channel_info(ch_index)
        next(self.gen_update_current_channel_info)
