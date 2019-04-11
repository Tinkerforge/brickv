# -*- coding: utf-8 -*-
"""
Industrial Dual 0-20mA 2.0 Plugin
Copyright (C) 2018 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

industrial_dual_0_20ma_v2.py: Industrial Dual 0-20ma V2 Plugin Implementation

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

from PyQt5.QtCore import Qt, QSize, QObject
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QGridLayout, \
                        QFrame, QSizePolicy, QDoubleSpinBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_industrial_dual_0_20ma_v2 import BrickletIndustrialDual020mAV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

CH_0 = 0
CH_1 = 1

class FixedSizeLabel(QLabel):
    maximum_size_hint = None

    def sizeHint(self):
        hint = QLabel.sizeHint(self)

        if self.maximum_size_hint != None:
            hint = QSize(max(hint.width(), self.maximum_size_hint.width()),
                         max(hint.height(), self.maximum_size_hint.height()))

        self.maximum_size_hint = hint

        return hint

class IndustrialDual020mAV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletIndustrialDual020mAV2, *args)

        self.dual020 = self.device

        self.str_connected = 'Channel {0} is <font color="green">connected</font>'
        self.str_not_connected = 'Channel {0} is <font color="red">not connected</font>'

        self.cbe_current0 = CallbackEmulator(functools.partial(self.dual020.get_current, CH_0),
                                             functools.partial(self.cb_current, CH_0),
                                             self.increase_error_count)
        self.cbe_current1 = CallbackEmulator(functools.partial(self.dual020.get_current, CH_1),
                                             functools.partial(self.cb_current, CH_1),
                                             self.increase_error_count)

        self.connected_labels = [FixedSizeLabel(self.str_not_connected.format(CH_0)),
                                 FixedSizeLabel(self.str_not_connected.format(CH_1))]

        self.current_current = [CurveValueWrapper(), CurveValueWrapper()] # float, mA

        plots = [('Channel 0',
                  Qt.red,
                  self.current_current[CH_0],
                  lambda value: '{:.03f} mA'.format(round(value, 3))),
                 ('Channel 1',
                  Qt.blue,
                  self.current_current[CH_1],
                  lambda value: '{:.03f} mA'.format(round(value, 3)))]

        self.plot_widget = PlotWidget('Current [mA]', plots,
                                      extra_key_widgets=self.connected_labels, y_resolution=0.001)

        h_sp = QSizePolicy()
        h_sp.setHorizontalPolicy(QSizePolicy.Expanding)

        self.sample_rate_label = QLabel('Sample Rate:')
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItem('240 Hz')
        self.sample_rate_combo.addItem('60 Hz')
        self.sample_rate_combo.addItem('15 Hz')
        self.sample_rate_combo.addItem('4 Hz')
        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)
        self.sample_rate_combo.setSizePolicy(h_sp)

        self.gain_label = QLabel('Gain:')
        self.gain_combo = QComboBox()
        self.gain_combo.addItem('x1')
        self.gain_combo.addItem('x2')
        self.gain_combo.addItem('x4')
        self.gain_combo.addItem('x8')
        self.gain_combo.currentIndexChanged.connect(self.gain_combo_index_changed)
        self.gain_combo.setSizePolicy(h_sp)

        self.led_config_ch0_label = QLabel('Channel 0')
        self.led_config_ch1_label = QLabel('Channel 1')
        self.led_config_label = QLabel('LED Config:')
        self.led_status_config_label = QLabel('LED Status Config:')
        self.led_status_config_ch0_min_label = QLabel('Min:')
        self.led_status_config_ch0_max_label = QLabel('Max:')
        self.led_status_config_ch1_min_label = QLabel('Min:')
        self.led_status_config_ch1_max_label = QLabel('Max:')

        self.led_config_ch0_combo = QComboBox()
        self.led_config_ch0_combo.addItem('Off')
        self.led_config_ch0_combo.addItem('On')
        self.led_config_ch0_combo.addItem('Show Heartbeat')
        self.led_config_ch0_combo.addItem('Show Channel Status')
        self.led_config_ch0_combo.setSizePolicy(h_sp)
        self.led_config_ch0_combo.currentIndexChanged.connect(self.led_config_ch0_combo_changed)

        self.led_config_ch1_combo = QComboBox()
        self.led_config_ch1_combo.addItem('Off')
        self.led_config_ch1_combo.addItem('On')
        self.led_config_ch1_combo.addItem('Show Heartbeat')
        self.led_config_ch1_combo.addItem('Show Channel Status')
        self.led_config_ch1_combo.setSizePolicy(h_sp)
        self.led_config_ch1_combo.currentIndexChanged.connect(self.led_config_ch1_combo_changed)

        self.led_status_config_ch0_combo = QComboBox()
        self.led_status_config_ch0_combo.addItem('Threshold')
        self.led_status_config_ch0_combo.addItem('Intensity')
        self.led_status_config_ch0_combo.setSizePolicy(h_sp)
        self.led_status_config_ch0_combo.currentIndexChanged.connect(self.led_status_config_ch0_combo_changed)

        self.led_status_config_ch1_combo = QComboBox()
        self.led_status_config_ch1_combo.addItem('Threshold')
        self.led_status_config_ch1_combo.addItem('Intensity')
        self.led_status_config_ch1_combo.setSizePolicy(h_sp)
        self.led_status_config_ch1_combo.currentIndexChanged.connect(self.led_status_config_ch1_combo_changed)

        self.led_status_config_ch0_min_sbox = QDoubleSpinBox()
        self.led_status_config_ch0_max_sbox = QDoubleSpinBox()
        self.led_status_config_ch1_min_sbox = QDoubleSpinBox()
        self.led_status_config_ch1_max_sbox = QDoubleSpinBox()

        self.led_status_config_ch0_min_sbox.setValue(0)
        self.led_status_config_ch0_min_sbox.setMinimum(0)
        self.led_status_config_ch0_min_sbox.setSingleStep(0.5)
        self.led_status_config_ch0_min_sbox.setDecimals(3)
        self.led_status_config_ch0_min_sbox.setSuffix(' mA')
        self.led_status_config_ch0_min_sbox.setMaximum(22.5)
        self.led_status_config_ch0_min_sbox.valueChanged.connect(self.led_status_config_ch0_min_sbox_changed)

        self.led_status_config_ch0_max_sbox.setValue(0)
        self.led_status_config_ch0_max_sbox.setMinimum(0)
        self.led_status_config_ch0_max_sbox.setSingleStep(0.5)
        self.led_status_config_ch0_max_sbox.setDecimals(3)
        self.led_status_config_ch0_max_sbox.setSuffix(' mA')
        self.led_status_config_ch0_max_sbox.setMaximum(22.5)
        self.led_status_config_ch0_max_sbox.valueChanged.connect(self.led_status_config_ch0_max_sbox_changed)

        self.led_status_config_ch1_min_sbox.setValue(0)
        self.led_status_config_ch1_min_sbox.setMinimum(0)
        self.led_status_config_ch1_min_sbox.setSingleStep(0.5)
        self.led_status_config_ch1_min_sbox.setDecimals(3)
        self.led_status_config_ch1_min_sbox.setSuffix(' mA')
        self.led_status_config_ch1_min_sbox.setMaximum(22.5)
        self.led_status_config_ch1_min_sbox.valueChanged.connect(self.led_status_config_ch1_min_sbox_changed)

        self.led_status_config_ch1_max_sbox.setValue(0)
        self.led_status_config_ch1_max_sbox.setMinimum(0)
        self.led_status_config_ch1_max_sbox.setSingleStep(0.5)
        self.led_status_config_ch1_max_sbox.setDecimals(3)
        self.led_status_config_ch1_max_sbox.setSuffix(' mA')
        self.led_status_config_ch1_max_sbox.setMaximum(22.5)
        self.led_status_config_ch1_max_sbox.valueChanged.connect(self.led_status_config_ch1_max_sbox_changed)

        hlayout = QHBoxLayout()
        self.led_status_config_ch0_min_sbox.setSizePolicy(h_sp)
        self.led_status_config_ch0_max_sbox.setSizePolicy(h_sp)
        hlayout.addWidget(self.led_status_config_ch0_min_label)
        hlayout.addWidget(self.led_status_config_ch0_min_sbox)
        hlayout.addWidget(self.led_status_config_ch0_max_label)
        hlayout.addWidget(self.led_status_config_ch0_max_sbox)

        hlayout1 = QHBoxLayout()
        self.led_status_config_ch1_min_sbox.setSizePolicy(h_sp)
        self.led_status_config_ch1_max_sbox.setSizePolicy(h_sp)
        hlayout1.addWidget(self.led_status_config_ch1_min_label)
        hlayout1.addWidget(self.led_status_config_ch1_min_sbox)
        hlayout1.addWidget(self.led_status_config_ch1_max_label)
        hlayout1.addWidget(self.led_status_config_ch1_max_sbox)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        line1 = QFrame()
        line1.setObjectName("line1")
        line1.setFrameShape(QFrame.HLine)
        line1.setFrameShadow(QFrame.Sunken)

        line2 = QFrame()
        line2.setObjectName("line2")
        line2.setFrameShape(QFrame.HLine)
        line2.setFrameShadow(QFrame.Sunken)

        glayout = QGridLayout()

        glayout.addWidget(line, 0, 0, 1, 3) # line-1
        glayout.addWidget(self.sample_rate_label, 1, 0, 1, 1)
        glayout.addWidget(self.sample_rate_combo, 1, 1, 1, 2)
        glayout.addWidget(self.gain_label, 2, 0, 1, 1)
        glayout.addWidget(self.gain_combo, 2, 1, 1, 2)
        glayout.addWidget(line1, 3, 0, 1, 3) # line-2
        glayout.addWidget(self.led_config_ch0_label, 4, 1, 1, 1)
        glayout.addWidget(self.led_config_ch1_label, 4, 2, 1, 1)
        glayout.addWidget(line2, 5, 0, 1, 3) # line-3
        glayout.addWidget(self.led_config_label, 6, 0, 1, 1)
        glayout.addWidget(self.led_config_ch0_combo, 6, 1, 1, 1)
        glayout.addWidget(self.led_config_ch1_combo, 6, 2, 1, 1)
        glayout.addWidget(self.led_status_config_label, 7, 0, 1, 1)
        glayout.addWidget(self.led_status_config_ch0_combo, 7, 1, 1, 1)
        glayout.addWidget(self.led_status_config_ch1_combo, 7, 2, 1, 1)
        glayout.addLayout(hlayout, 8, 1, 1, 1)
        glayout.addLayout(hlayout1, 8, 2, 1, 1)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addLayout(glayout)

        self.ui_group_ch_status_ch0 = [self.led_status_config_ch0_combo,
                                       self.led_status_config_ch0_min_sbox,
                                       self.led_status_config_ch0_max_sbox]

        self.ui_group_ch_status_ch1 = [self.led_status_config_ch1_combo,
                                       self.led_status_config_ch1_min_sbox,
                                       self.led_status_config_ch1_max_sbox]

    def start(self):
        async_call(self.dual020.get_sample_rate,
                   None,
                   self.get_sample_rate_async,
                   self.increase_error_count)

        async_call(self.dual020.get_gain,
                   None,
                   self.get_gain_async,
                   self.increase_error_count)

        async_call(self.dual020.get_channel_led_config,
                   CH_0,
                   lambda config: self.get_channel_led_config_async(CH_0, config),
                   self.increase_error_count)

        async_call(self.dual020.get_channel_led_status_config,
                   CH_0,
                   lambda config: self.get_channel_led_status_config_async(CH_0, config),
                   self.increase_error_count)

        async_call(self.dual020.get_channel_led_config,
                   CH_1,
                   lambda config: self.get_channel_led_config_async(CH_1, config),
                   self.increase_error_count)

        async_call(self.dual020.get_channel_led_status_config,
                   CH_1,
                   lambda config: self.get_channel_led_status_config_async(CH_1, config),
                   self.increase_error_count)

        self.cbe_current0.set_period(100)
        self.cbe_current1.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_current0.set_period(0)
        self.cbe_current1.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDual020mAV2.DEVICE_IDENTIFIER

    def sample_rate_combo_index_changed(self, index):
        async_call(self.dual020.set_sample_rate,
                   index,
                   None,
                   self.increase_error_count)

    def gain_combo_index_changed(self, index):
        async_call(self.dual020.set_gain,
                   index,
                   None,
                   self.increase_error_count)

    def led_status_config_ch0_min_sbox_changed(self, _value):
        QObject.sender(self).blockSignals(True)

        self.dual020.set_channel_led_status_config(CH_0,
                                                   self.led_status_config_ch0_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch0_max_sbox.value() * 1000000,
                                                   self.led_status_config_ch0_combo.currentIndex())

        QObject.sender(self).blockSignals(False)

    def led_status_config_ch0_max_sbox_changed(self, _value):
        QObject.sender(self).blockSignals(True)

        self.dual020.set_channel_led_status_config(CH_0,
                                                   self.led_status_config_ch0_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch0_max_sbox.value() * 1000000,
                                                   self.led_status_config_ch0_combo.currentIndex())

        QObject.sender(self).blockSignals(False)

    def led_status_config_ch1_min_sbox_changed(self, _value):
        QObject.sender(self).blockSignals(True)


        self.dual020.set_channel_led_status_config(CH_1,
                                                   self.led_status_config_ch1_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch1_max_sbox.value() * 1000000,
                                                   self.led_status_config_ch1_combo.currentIndex())

        QObject.sender(self).blockSignals(False)

    def led_status_config_ch1_max_sbox_changed(self, _value):
        QObject.sender(self).blockSignals(True)

        self.dual020.set_channel_led_status_config(CH_1,
                                                   self.led_status_config_ch1_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch1_max_sbox.value() * 1000000,
                                                   self.led_status_config_ch1_combo.currentIndex())

        QObject.sender(self).blockSignals(False)

    def led_status_config_ch0_combo_changed(self, index):
        self.dual020.set_channel_led_status_config(CH_0,
                                                   self.led_status_config_ch0_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch0_max_sbox.value() * 1000000,
                                                   index)

    def led_status_config_ch1_combo_changed(self, index):
        self.dual020.set_channel_led_status_config(CH_1,
                                                   self.led_status_config_ch1_min_sbox.value() * 1000000,
                                                   self.led_status_config_ch1_max_sbox.value() * 1000000,
                                                   index)

    def led_config_ch0_combo_changed(self, index):
        if index != self.dual020.CHANNEL_LED_CONFIG_SHOW_CHANNEL_STATUS:
            for e in self.ui_group_ch_status_ch0:
                e.setEnabled(False)
        else:
            for e in self.ui_group_ch_status_ch0:
                e.setEnabled(True)

        self.dual020.set_channel_led_config(CH_0, index)

    def led_config_ch1_combo_changed(self, index):
        if index != self.dual020.CHANNEL_LED_CONFIG_SHOW_CHANNEL_STATUS:
            for e in self.ui_group_ch_status_ch1:
                e.setEnabled(False)
        else:
            for e in self.ui_group_ch_status_ch1:
                e.setEnabled(True)

        self.dual020.set_channel_led_config(CH_1, index)

    def cb_current(self, channel, current):
        value = current / 1000000.0
        self.current_current[channel].value = value

        if value < 3.9:
            self.connected_labels[channel].setText(self.str_not_connected.format(channel))
        else:
            self.connected_labels[channel].setText(self.str_connected.format(channel))

    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.setCurrentIndex(rate)

    def get_gain_async(self, rate):
        self.gain_combo.setCurrentIndex(rate)

    def get_channel_led_config_async(self, channel, config):
        if channel == CH_0:
            self.led_config_ch0_combo.setCurrentIndex(config)
            self.led_config_ch0_combo_changed(config)
        elif channel == CH_1:
            self.led_config_ch1_combo.setCurrentIndex(config)
            self.led_config_ch1_combo_changed(config)

    def get_channel_led_status_config_async(self, channel, config):
        if channel == CH_0:
            self.led_status_config_ch0_combo.setCurrentIndex(config.config)
            self.led_status_config_ch0_combo_changed(config.config)
            self.led_status_config_ch0_max_sbox.setValue(config.max / 1000000.0)
            self.led_status_config_ch0_min_sbox.setValue(config.min / 1000000.0)
        elif channel == CH_1:
            self.led_status_config_ch1_combo.setCurrentIndex(config.config)
            self.led_status_config_ch1_combo_changed(config.config)
            self.led_status_config_ch1_max_sbox.setValue(config.max / 1000000.0)
            self.led_status_config_ch1_min_sbox.setValue(config.min / 1000000.0)
