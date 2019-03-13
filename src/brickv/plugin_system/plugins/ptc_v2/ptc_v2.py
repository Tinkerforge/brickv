# -*- coding: utf-8 -*-
"""
PTC 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

ptc_v2.py: PTC 2.0 Plugin Implementation

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

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QFrame

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_ptc_v2 import BrickletPTCV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator


class PTCV2(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletPTCV2, *args)

        self.ptc = self.device

        self.str_connected = 'Sensor is <font color="green">connected</font>'
        self.str_not_connected = 'Sensor is <font color="red">not connected</font>'

        self.cbe_temperature = CallbackEmulator(self.ptc.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.wire_label = QLabel('Wire Type:')
        self.wire_combo = QComboBox()
        self.wire_combo.addItem('2-Wire')
        self.wire_combo.addItem('3-Wire')
        self.wire_combo.addItem('4-Wire')

        self.noise_label = QLabel('Noise Rejection Filter:')
        self.noise_combo = QComboBox()
        self.noise_combo.addItem('50 Hz')
        self.noise_combo.addItem('60 Hz')

        self.connected_label = QLabel(self.str_connected)

        self.current_temperature = None # float, °C

        self.wire_combo.currentIndexChanged.connect(self.wire_combo_index_changed)
        self.noise_combo.currentIndexChanged.connect(self.noise_combo_index_changed)

        plots = [('Temperature', Qt.red, lambda: self.current_temperature, '{} °C'.format)]
        self.plot_widget = PlotWidget('Temperature [°C]', plots, extra_key_widgets=[self.connected_label])

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.wire_label)
        hlayout.addWidget(self.wire_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.noise_label)
        hlayout.addWidget(self.noise_combo)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

        self.connected_timer = QTimer()
        self.connected_timer.timeout.connect(self.update_connected)
        self.connected_timer.setInterval(1000)

    def start(self):
        async_call(self.ptc.get_temperature, None, self.cb_temperature, self.increase_error_count)
        self.cbe_temperature.set_period(100)

        async_call(self.ptc.is_sensor_connected, None, self.is_sensor_connected_async, self.increase_error_count)
        async_call(self.ptc.get_noise_rejection_filter, None, self.get_noise_rejection_filter_async, self.increase_error_count)
        async_call(self.ptc.get_wire_mode, None, self.get_wire_mode_async, self.increase_error_count)

        self.connected_timer.start()
        self.plot_widget.stop = False

    def stop(self):
        self.cbe_temperature.set_period(0)

        self.connected_timer.stop()
        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPTCV2.DEVICE_IDENTIFIER

    def update_connected(self):
        async_call(self.ptc.is_sensor_connected, None, self.is_sensor_connected_async, self.increase_error_count)

    def wire_combo_index_changed(self, index):
        async_call(self.ptc.set_wire_mode, index+2, None, self.increase_error_count)

    def noise_combo_index_changed(self, index):
        async_call(self.ptc.set_noise_rejection_filter, index, None, self.increase_error_count)

    def is_sensor_connected_async(self, connected):
        if connected:
            self.connected_label.setText(self.str_connected)
        else:
            self.connected_label.setText(self.str_not_connected)

    def get_noise_rejection_filter_async(self, filter_option):
        self.noise_combo.setCurrentIndex(filter_option)

    def get_wire_mode_async(self, mode):
        self.wire_combo.setCurrentIndex(mode-2)

    def cb_temperature(self, temperature):
        self.current_temperature = temperature / 100.0

    def cb_resistance(self, resistance):
        resistance_str = str(round(resistance * 3900.0 / (1 << 15), 1))
        self.resistance_label.setText(resistance_str)
