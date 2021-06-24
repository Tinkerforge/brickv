# -*- coding: utf-8 -*-
"""
Industrial Counter Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

industrial_counter.py: Industrial Counter Plugin Implementation

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

from PyQt5.QtCore import Qt

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.industrial_counter.ui_industrial_counter import Ui_IndustrialCounter
from brickv.bindings.bricklet_industrial_counter import BrickletIndustrialCounter
from brickv.callback_emulator import CallbackEmulator
from brickv.async_call import async_call

class IndustrialCounter(COMCUPluginBase, Ui_IndustrialCounter):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialCounter, *args)

        self.setupUi(self)

        self.counter = self.device

        self.cbe_signal = CallbackEmulator(self,
                                           self.counter.get_all_signal_data,
                                           None,
                                           self.cb_all_signal_data,
                                           self.increase_error_count)

        self.cbe_counter = CallbackEmulator(self,
                                            self.counter.get_all_counter,
                                            None,
                                            self.cb_all_counter,
                                            self.increase_error_count)

        def get_combo_lambda(channel):
            return lambda: self.combo_index_changed(channel)

        def get_checkstate_lambda(channel):
            return lambda x: self.checkstate_changed(channel, x)

        g = self.main_grid
        pos = 2
        self.checkboxess_active = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        for channel, checkbox in enumerate(self.checkboxess_active):
            checkbox.stateChanged.connect(get_checkstate_lambda(channel))

        pos += 1
        self.combos_count_edge = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        for channel, combo in enumerate(self.combos_count_edge):
            combo.addItem('Rising')
            combo.addItem('Falling')
            combo.addItem('Both')
            combo.currentIndexChanged.connect(get_combo_lambda(channel))

        pos += 1
        self.combos_count_direction = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        for channel, combo in enumerate(self.combos_count_direction):
            combo.addItem('Up')
            combo.addItem('Down')
            combo.currentIndexChanged.connect(get_combo_lambda(channel))

        self.combos_count_direction[0].addItem('Ext Up (Ch 2)')
        self.combos_count_direction[0].addItem('Ext Down (Ch 2)')
        self.combos_count_direction[3].addItem('Ext Up (Ch 1)')
        self.combos_count_direction[3].addItem('Ext Down (Ch 1)')

        pos += 1
        self.combos_duty_cycle_prescaler = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        for channel, combo in enumerate(self.combos_duty_cycle_prescaler):
            combo.addItem('1')
            combo.addItem('2')
            combo.addItem('4')
            combo.addItem('8')
            combo.addItem('16')
            combo.addItem('32')
            combo.addItem('64')
            combo.addItem('128')
            combo.addItem('256')
            combo.addItem('512')
            combo.addItem('1024')
            combo.addItem('2048')
            combo.addItem('4096')
            combo.addItem('8192')
            combo.addItem('16384')
            combo.addItem('32768')
            combo.currentIndexChanged.connect(get_combo_lambda(channel))

        pos += 1
        self.combos_frequency_integration = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        for channel, combo in enumerate(self.combos_frequency_integration):
            combo.addItem('128ms')
            combo.addItem('256ms')
            combo.addItem('512ms')
            combo.addItem('1024ms')
            combo.addItem('2048ms')
            combo.addItem('4096ms')
            combo.addItem('8192ms')
            combo.addItem('16384ms')
            combo.addItem('32768ms')
            combo.currentIndexChanged.connect(get_combo_lambda(channel))

        pos += 3
        self.labels_counter    = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]
        pos += 1
        self.labels_duty_cycle = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]
        pos += 1
        self.labels_period     = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]
        pos += 1
        self.labels_frequency  = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]
        pos += 1
        self.labels_value      = [g.itemAtPosition(pos, 1).widget(), g.itemAtPosition(pos, 2).widget(), g.itemAtPosition(pos, 3).widget(), g.itemAtPosition(pos, 4).widget()]

        self.cbox_cs0_cfg.currentIndexChanged.connect(self.cbox_cs0_cfg_changed)
        self.cbox_cs1_cfg.currentIndexChanged.connect(self.cbox_cs1_cfg_changed)
        self.cbox_cs2_cfg.currentIndexChanged.connect(self.cbox_cs2_cfg_changed)
        self.cbox_cs3_cfg.currentIndexChanged.connect(self.cbox_cs3_cfg_changed)

    def cbox_cs0_cfg_changed(self, idx):
        self.counter.set_channel_led_config(0, idx)

    def cbox_cs1_cfg_changed(self, idx):
        self.counter.set_channel_led_config(1, idx)

    def cbox_cs2_cfg_changed(self, idx):
        self.counter.set_channel_led_config(2, idx)

    def cbox_cs3_cfg_changed(self, idx):
        self.counter.set_channel_led_config(3, idx)

    def async_get_channel_led_config(self, idx, cfg):
        if idx == 0:
            self.cbox_cs0_cfg.setCurrentIndex(cfg)
        elif idx == 1:
            self.cbox_cs1_cfg.setCurrentIndex(cfg)
        elif idx == 2:
            self.cbox_cs2_cfg.setCurrentIndex(cfg)
        elif idx == 3:
            self.cbox_cs3_cfg.setCurrentIndex(cfg)

    def cb_all_signal_data(self, data):
        for i in range(4):
            duty_cycle_str = "{:2.2f} %".format(data.duty_cycle[i] / 100.0)
            self.labels_duty_cycle[i].setText(duty_cycle_str)

            if data.period[i] > 900 * 1000 * 1000:
                period_str = "{:.3f} s".format(data.period[i] / (1000 * 1000 * 1000.0))
            elif data.period[i] > 900 * 1000:
                period_str = "{:.3f} ms".format(data.period[i] / (1000 * 1000.0))
            elif data.period[i] > 900:
                period_str = "{:.3f} us".format(data.period[i] / 1000.0)
            else:
                period_str = "{} ns".format(data.period[i])

            self.labels_period[i].setText(period_str)

            if data.frequency[i] > 900 * 1000 * 1000:
                frequency_str = "{:.3f} MHz".format(data.frequency[i] / (1000 * 1000 * 1000.0))
            elif data.frequency[i] > 900 * 1000:
                frequency_str = "{:.3f} kHz".format(data.frequency[i] / (1000 * 1000.0))
            else:
                frequency_str = "{:.3f} Hz".format(data.frequency[i] / 1000.0)

            self.labels_frequency[i].setText(frequency_str)
            self.labels_value[i].setText('High' if data.value[i] else 'Low')

    def cb_all_counter(self, data):
        for i in range(4):
            self.labels_counter[i].setText(str(data[i]))

    def combo_signals_block(self, channel):
        self.combos_count_edge[channel].blockSignals(True)
        self.combos_count_direction[channel].blockSignals(True)
        self.combos_duty_cycle_prescaler[channel].blockSignals(True)
        self.combos_frequency_integration[channel].blockSignals(True)

    def combo_signals_release(self, channel):
        self.combos_count_edge[channel].blockSignals(False)
        self.combos_count_direction[channel].blockSignals(False)
        self.combos_duty_cycle_prescaler[channel].blockSignals(False)
        self.combos_frequency_integration[channel].blockSignals(False)

    def checkstate_changed(self, channel, value):
        self.counter.set_counter_active(channel, True if value == Qt.Checked else False)

    def combo_index_changed(self, channel):
        count_edge = self.combos_count_edge[channel].currentIndex()
        count_direction = self.combos_count_direction[channel].currentIndex()
        duty_cycle_prescaler = self.combos_duty_cycle_prescaler[channel].currentIndex()
        frequency_integration = self.combos_frequency_integration[channel].currentIndex()

        if duty_cycle_prescaler == 16:
            duty_cycle_prescaler = 255

        if frequency_integration == 9:
            frequency_integration = 255

        self.counter.set_counter_configuration(channel, count_edge, count_direction, duty_cycle_prescaler, frequency_integration)

    def get_all_counter_active_async(self, active):
        for i in range(4):
            self.checkboxess_active[i].blockSignals(True)
            if active[i]:
                self.checkboxess_active[i].setCheckState(Qt.Checked)
            else:
                self.checkboxess_active[i].setCheckState(Qt.Unchecked)
            self.checkboxess_active[i].blockSignals(False)

    def get_counter_configuration_async(self, channel, configuration):
        self.combo_signals_block(channel)
        self.combos_count_edge[channel].setCurrentIndex(configuration.count_edge)
        self.combos_count_direction[channel].setCurrentIndex(configuration.count_direction)
        self.combos_duty_cycle_prescaler[channel].setCurrentIndex(configuration.duty_cycle_prescaler if configuration.duty_cycle_prescaler != 255 else 16)
        self.combos_frequency_integration[channel].setCurrentIndex(configuration.frequency_integration_time if configuration.frequency_integration_time != 255 else 9)
        self.combo_signals_release(channel)

    def start(self):
        for channel in range(4):
            async_call(self.counter.get_counter_configuration, channel, self.get_counter_configuration_async, self.increase_error_count,
                       pass_arguments_to_result_callback=True)
            async_call(self.counter.get_channel_led_config, channel, self.async_get_channel_led_config, self.increase_error_count,
                       pass_arguments_to_result_callback=True)

        async_call(self.counter.get_all_counter_active, None, self.get_all_counter_active_async, self.increase_error_count)

        self.cbe_signal.set_period(50)
        self.cbe_counter.set_period(50)

    def stop(self):
        self.cbe_signal.set_period(0)
        self.cbe_counter.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialCounter.DEVICE_IDENTIFIER
