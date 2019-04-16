# -*- coding: utf-8 -*-
"""
Industrial Analog Out 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_analog_out_v2.py: Industrial Analog Out 2.0 Plugin Implementation

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
from brickv.plugin_system.plugins.industrial_analog_out_v2.ui_industrial_analog_out_v2 import Ui_IndustrialAnalogOutV2
from brickv.bindings.bricklet_industrial_analog_out_v2 import BrickletIndustrialAnalogOutV2
from brickv.async_call import async_call
from brickv.slider_spin_syncer import SliderSpinSyncer

class IndustrialAnalogOutV2(COMCUPluginBase, Ui_IndustrialAnalogOutV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIndustrialAnalogOutV2, *args)

        self.setupUi(self)

        self.ao = self.device

        self.voltage_syncer = SliderSpinSyncer(self.slider_voltage,
                                               self.spin_voltage,
                                               self.voltage_changed)

        self.current_syncer = SliderSpinSyncer(self.slider_current,
                                               self.spin_current,
                                               self.current_changed)

        self.radio_voltage.clicked.connect(self.radio_clicked)
        self.radio_current.clicked.connect(self.radio_clicked)

        self.box_voltage_range.currentIndexChanged.connect(self.config_changed)
        self.box_current_range.currentIndexChanged.connect(self.config_changed)

        self.checkbox_enable.clicked.connect(self.enable_changed)

        self.cbox_osl_lc.currentIndexChanged.connect(self.cbox_osl_lc_changed)
        self.cbox_osl_lsc.currentIndexChanged.connect(self.cbox_osl_lsc_changed)
        self.sbox_osl_min.valueChanged.connect(self.sbox_osl_min_changed)
        self.sbox_osl_max.valueChanged.connect(self.sbox_osl_max_changed)

        self.ui_grp_show_ch_status = [self.cbox_osl_lsc,
                                      self.sbox_osl_min,
                                      self.sbox_osl_max]

        self.box_voltage_range.setCurrentIndex(1)
        self.box_current_range.setCurrentIndex(0)

        self.new_voltage(0)
        self.new_current(0)
        self.mode_voltage()

    def start(self):
        async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
        async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)
        async_call(self.ao.get_enabled, None, self.get_enabled_async, self.increase_error_count)
        async_call(self.ao.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.ao.get_out_led_config, None, self.get_out_led_config_async, self.increase_error_count)

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialAnalogOutV2.DEVICE_IDENTIFIER

    def enable_changed(self, enabled):
        try:
            self.ao.set_enabled(enabled)
        except:
            return

        if self.cbox_osl_lc.currentIndex() < BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_OUT_STATUS:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

            return

        if enabled:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(True)
        else:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

    def cbox_osl_lc_changed(self, index):
        if index == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_OFF:
            try:
                self.ao.set_out_led_config(index)
            except:
                return

            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)
        elif index == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_ON:
            try:
                self.ao.set_out_led_config(index)
            except:
                return

            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)
        elif index == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_HEARTBEAT:
            try:
                self.ao.set_out_led_config(index)
            except:
                return

            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)
        elif index == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_OUT_STATUS:
            min = self.sbox_osl_min.value()
            max = self.sbox_osl_max.value()
            config = self.cbox_osl_lsc.currentIndex()

            try:
                self.ao.set_out_led_config(index)
                self.ao.set_out_led_status_config(min, max, config)
            except:
                return

            if self.checkbox_enable.isChecked():
                for e in self.ui_grp_show_ch_status:
                    e.setEnabled(True)

    def new_voltage(self, voltage):
        if voltage < self.slider_voltage.minimum():
            voltage = self.slider_voltage.minimum()
        elif voltage > self.slider_voltage.maximum():
            voltage = self.slider_voltage.maximum()

        try:
            self.ao.set_voltage(voltage)
        except:
            return

        self.spin_voltage.blockSignals(True)
        self.slider_voltage.blockSignals(True)

        self.spin_voltage.setValue(voltage)
        self.slider_voltage.setValue(voltage)

        self.spin_voltage.blockSignals(False)
        self.slider_voltage.blockSignals(False)

    def new_current(self, current):
        if current < self.slider_current.minimum():
            current = self.slider_current.minimum()
        elif current > self.slider_current.maximum():
            current = self.slider_current.maximum()

        try:
            self.ao.set_current(current)
        except:
            return

        self.spin_current.blockSignals(True)
        self.slider_current.blockSignals(True)

        self.spin_current.setValue(current)
        self.slider_current.setValue(current)

        self.spin_current.blockSignals(False)
        self.slider_current.blockSignals(False)

    def mode_voltage(self):
        self.widget_voltage.show()
        self.widget_current.hide()

    def mode_current(self):
        self.widget_voltage.hide()
        self.widget_current.show()

    def radio_clicked(self):
        if self.radio_voltage.isChecked():
            self.mode_voltage()
            async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
        else:
            self.mode_current()
            async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)

        async_call(self.ao.get_out_led_config, None, self.get_out_led_config_async, self.increase_error_count)

    def voltage_changed(self, value):
        try:
            self.ao.set_voltage(value)
        except:
            return

        self.new_voltage(value)

    def current_changed(self, value):
        try:
            self.ao.set_current(value)
        except:
            return

        self.new_current(value)

    def new_configuration(self):
        vr = self.box_voltage_range.currentIndex()
        cr = self.box_current_range.currentIndex()

        if vr == BrickletIndustrialAnalogOutV2.VOLTAGE_RANGE_0_TO_5V:
            self.spin_voltage.setMinimum(0)
            self.slider_voltage.setMinimum(0)
            self.spin_voltage.setMaximum(5000)
            self.slider_voltage.setMaximum(5000)
        elif vr == BrickletIndustrialAnalogOutV2.VOLTAGE_RANGE_0_TO_10V:
            self.spin_voltage.setMinimum(0)
            self.slider_voltage.setMinimum(0)
            self.spin_voltage.setMaximum(10000)
            self.slider_voltage.setMaximum(10000)

        if cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_4_TO_20MA:
            self.spin_current.setMinimum(4000)
            self.slider_current.setMinimum(4000)
            self.spin_current.setMaximum(20000)
            self.slider_current.setMaximum(20000)
        elif cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_0_TO_20MA:
            self.spin_current.setMinimum(0)
            self.slider_current.setMinimum(0)
            self.spin_current.setMaximum(20000)
            self.slider_current.setMaximum(20000)
        elif cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_0_TO_24MA:
            self.spin_current.setMinimum(0)
            self.slider_current.setMinimum(0)
            self.spin_current.setMaximum(24000)
            self.slider_current.setMaximum(24000)

    def update_led_status_config_gui(self, v):
        vr = self.box_voltage_range.currentIndex()
        cr = self.box_current_range.currentIndex()

        if v:
            if vr == BrickletIndustrialAnalogOutV2.VOLTAGE_RANGE_0_TO_5V:
                self.sbox_osl_min.setMinimum(0)
                self.sbox_osl_min.setMaximum(5000)
                self.sbox_osl_min.setSuffix(" mV")
                self.sbox_osl_max.setMinimum(0)
                self.sbox_osl_max.setMaximum(5000)
                self.sbox_osl_max.setSuffix(" mV")
            elif vr == BrickletIndustrialAnalogOutV2.VOLTAGE_RANGE_0_TO_10V:
                self.sbox_osl_min.setMinimum(0)
                self.sbox_osl_min.setMaximum(10000)
                self.sbox_osl_min.setSuffix(" mV")
                self.sbox_osl_max.setMinimum(0)
                self.sbox_osl_max.setMaximum(10000)
                self.sbox_osl_max.setSuffix(" mV")
        else:
            if cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_4_TO_20MA:
                self.sbox_osl_min.setMinimum(4000)
                self.sbox_osl_min.setMaximum(20000)
                self.sbox_osl_min.setSuffix(u" µA")
                self.sbox_osl_max.setMinimum(4000)
                self.sbox_osl_max.setMaximum(20000)
                self.sbox_osl_max.setSuffix(u" µA")
            elif cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_0_TO_20MA:
                self.sbox_osl_min.setMinimum(0)
                self.sbox_osl_min.setMaximum(20000)
                self.sbox_osl_min.setSuffix(u" µA")
                self.sbox_osl_max.setMinimum(0)
                self.sbox_osl_max.setMaximum(20000)
                self.sbox_osl_max.setSuffix(u" µA")
            elif cr == BrickletIndustrialAnalogOutV2.CURRENT_RANGE_0_TO_24MA:
                self.sbox_osl_min.setMinimum(0)
                self.sbox_osl_min.setMaximum(24000)
                self.sbox_osl_min.setSuffix(u" µA")
                self.sbox_osl_max.setMinimum(0)
                self.sbox_osl_max.setMaximum(24000)
                self.sbox_osl_max.setSuffix(u" µA")

    def config_changed(self, value):
        try:
            self.ao.set_configuration(self.box_voltage_range.currentIndex(),
                                      self.box_current_range.currentIndex())

        except:
            return

        self.new_configuration()
        self.update_led_status_config_gui(self.radio_voltage.isChecked())

        async_call(self.ao.get_voltage, None, self.new_voltage, self.increase_error_count)
        async_call(self.ao.get_current, None, self.new_current, self.increase_error_count)

    def get_configuration_async(self, conf):
        self.box_voltage_range.setCurrentIndex(conf.voltage_range)
        self.box_current_range.setCurrentIndex(conf.current_range)
        self.new_configuration()

    def get_enabled_async(self, enabled):
        self.checkbox_enable.setChecked(enabled)

        if enabled:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(True)
        else:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

    def get_out_led_config_async(self, config):
        if config == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_OFF:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

            self.cbox_osl_lc.setCurrentIndex(config)

        elif config == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_ON:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

            self.cbox_osl_lc.setCurrentIndex(config)

        elif config == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_HEARTBEAT:
            for e in self.ui_grp_show_ch_status:
                e.setEnabled(False)

            self.cbox_osl_lc.setCurrentIndex(config)

        elif config == BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_OUT_STATUS:
            async_call(self.ao.get_out_led_status_config, None, self.cb_get_out_led_status_config, self.increase_error_count)

            if self.checkbox_enable.isChecked():
                for e in self.ui_grp_show_ch_status:
                    e.setEnabled(True)

    def cb_get_out_led_status_config(self, config):
        self.cbox_osl_lc.blockSignals(True)
        self.cbox_osl_lsc.blockSignals(True)
        self.sbox_osl_min.blockSignals(True)
        self.sbox_osl_max.blockSignals(True)

        self.cbox_osl_lsc.setCurrentIndex(config.config)
        self.cbox_osl_lc.setCurrentIndex(BrickletIndustrialAnalogOutV2.OUT_LED_CONFIG_SHOW_OUT_STATUS)
        self.update_led_status_config_gui(self.radio_voltage.isChecked())

        self.sbox_osl_min.setValue(config.min)
        self.sbox_osl_max.setValue(config.max)

        self.cbox_osl_lc.blockSignals(False)
        self.cbox_osl_lsc.blockSignals(False)
        self.sbox_osl_min.blockSignals(False)
        self.sbox_osl_max.blockSignals(False)

    def cbox_osl_lsc_changed(self, value):
        try:
            self.ao.set_out_led_status_config(self.sbox_osl_min.value(),
                                              self.sbox_osl_max.value(),
                                              value)
        except:
            pass

    def sbox_osl_min_changed(self, value):
        try:
            self.ao.set_out_led_status_config(value,
                                              self.sbox_osl_max.value(),
                                              self.cbox_osl_lsc.currentIndex())
        except:
            pass

    def sbox_osl_max_changed(self, value):
        try:
            self.ao.set_out_led_status_config(self.sbox_osl_min.value(),
                                              value,
                                              self.cbox_osl_lsc.currentIndex())
        except:
            pass
