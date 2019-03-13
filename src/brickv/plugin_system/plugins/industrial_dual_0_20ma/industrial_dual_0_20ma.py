# -*- coding: utf-8 -*-
"""
Industrial Dual 0-20mA Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

industrial_dual_0_20ma.py: PTC Plugin Implementation

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

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_industrial_dual_0_20ma import BrickletIndustrialDual020mA
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class FixedSizeLabel(QLabel):
    maximum_size_hint = None

    def sizeHint(self):
        hint = QLabel.sizeHint(self)

        if self.maximum_size_hint != None:
            hint = QSize(max(hint.width(), self.maximum_size_hint.width()),
                         max(hint.height(), self.maximum_size_hint.height()))

        self.maximum_size_hint = hint

        return hint

class IndustrialDual020mA(PluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletIndustrialDual020mA, *args)

        self.dual020 = self.device

        self.str_connected = 'Sensor {0} is <font color="green">connected</font>'
        self.str_not_connected = 'Sensor {0} is <font color="red">not connected</font>'

        self.cbe_current0 = CallbackEmulator(functools.partial(self.dual020.get_current, 0),
                                             functools.partial(self.cb_current, 0),
                                             self.increase_error_count)
        self.cbe_current1 = CallbackEmulator(functools.partial(self.dual020.get_current, 1),
                                             functools.partial(self.cb_current, 1),
                                             self.increase_error_count)

        self.connected_labels = [FixedSizeLabel(self.str_not_connected.format(0)),
                                 FixedSizeLabel(self.str_not_connected.format(1))]

        self.current_current = [None, None] # float, mA

        plots = [('Sensor 0', Qt.red, lambda: self.current_current[0], lambda value: '{:.02f} mA'.format(round(value, 2))),
                 ('Sensor 1', Qt.blue, lambda: self.current_current[1], lambda value: '{:.02f} mA'.format(round(value, 2)))]
        self.plot_widget = PlotWidget('Current [mA]', plots, extra_key_widgets=self.connected_labels)

        self.sample_rate_label = QLabel('Sample Rate:')
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItem('240 Hz')
        self.sample_rate_combo.addItem('60 Hz')
        self.sample_rate_combo.addItem('15 Hz')
        self.sample_rate_combo.addItem('4 Hz')
        self.sample_rate_combo.currentIndexChanged.connect(self.sample_rate_combo_index_changed)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.sample_rate_label)
        hlayout.addWidget(self.sample_rate_combo)
        hlayout.addStretch()

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def start(self):
        async_call(self.dual020.get_current, 0, lambda x: self.cb_current(0, x), self.increase_error_count)
        async_call(self.dual020.get_current, 1, lambda x: self.cb_current(1, x), self.increase_error_count)
        self.cbe_current0.set_period(100)
        self.cbe_current1.set_period(100)

        async_call(self.dual020.get_sample_rate, None, self.get_sample_rate_async, self.increase_error_count)
        self.plot_widget.stop = False

    def stop(self):
        self.cbe_current0.set_period(0)
        self.cbe_current1.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDual020mA.DEVICE_IDENTIFIER

    def sample_rate_combo_index_changed(self, index):
        async_call(self.dual020.set_sample_rate, index, None, self.increase_error_count)

    def get_sample_rate_async(self, rate):
        self.sample_rate_combo.setCurrentIndex(rate)

    def cb_current(self, sensor, current):
        value = current / 1000000.0
        self.current_current[sensor] = value

        if value < 3.9:
            self.connected_labels[sensor].setText(self.str_not_connected.format(sensor))
        else:
            self.connected_labels[sensor].setText(self.str_connected.format(sensor))
