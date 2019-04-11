# -*- coding: utf-8 -*-
"""
Gas Detector Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015-2016 Matthias Bolte <matthias@tinkerforge.com>

gas_detector.py: Gas Detector Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QCheckBox, QComboBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_gas_detector import BrickletGasDetector
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class GasDetector(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletGasDetector, *args)

        self.gas_detector = self.device

        self.cbe_value = CallbackEmulator(self.gas_detector.get_value,
                                          self.cb_value,
                                          self.increase_error_count)

        self.current_value = CurveValueWrapper()

        plots = [('Value', Qt.red, self.current_value, str)]
        self.plot_widget = PlotWidget('Value', plots, y_resolution=1.0)

        self.heater_checkbox = QCheckBox()
        self.heater_checkbox.setText('Heater')

        self.type_combo = QComboBox()
        self.type_combo.addItem('Type 0 (MQ2, MQ5)')
        self.type_combo.addItem('Type 1 (MQ3)')

        self.type_combo.currentIndexChanged.connect(self.type_combo_index_changed)
        self.heater_checkbox.stateChanged.connect(self.heater_checkbox_state_changed)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Detector Type:'))
        hlayout.addWidget(self.type_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.heater_checkbox)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def heater_checkbox_state_changed(self, state):
        if state == Qt.Unchecked:
            self.gas_detector.heater_off()
        elif state == Qt.Checked:
            self.gas_detector.heater_on()

    def type_combo_index_changed(self, index):
        async_call(self.gas_detector.set_detector_type, index, None, self.increase_error_count)

    def get_detector_type_async(self, detector_type):
        self.type_combo.setCurrentIndex(detector_type)

    def is_heater_on_async(self, heater):
        if heater:
            self.heater_checkbox.setChecked(True)
        else:
            self.heater_checkbox.setChecked(False)

    def cb_value(self, value):
        self.current_value.value = value

    def start(self):
        async_call(self.gas_detector.get_detector_type, None, self.get_detector_type_async, self.increase_error_count)
        async_call(self.gas_detector.is_heater_on, None, self.is_heater_on_async, self.increase_error_count)

        self.cbe_value.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_value.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletGasDetector.DEVICE_IDENTIFIER
