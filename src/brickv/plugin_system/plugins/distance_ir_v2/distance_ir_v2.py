# -*- coding: utf-8 -*-
"""
Distance IR 2.0 Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

distance_ir_v2.py: Distance IR 2.0 Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, \
                            QFrame, QSpinBox, QComboBox

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_distance_ir_v2 import BrickletDistanceIRV2
from brickv.plot_widget import PlotWidget, CurveValueWrapper, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class AnalogLabel(FixedSizeLabel):
    def setText(self, text):
        text = "Analog Value: " + str(text)
        super().setText(text)

class DistanceIRV2(COMCUPluginBase):
    NUM_VALUES = 512
    DIVIDER = 2**12//NUM_VALUES

    def __init__(self, *args):
        super().__init__(BrickletDistanceIRV2, *args)

        self.dist = self.device

        self.cbe_distance = CallbackEmulator(self.dist.get_distance,
                                             None,
                                             self.cb_distance,
                                             self.increase_error_count)
        self.cbe_analog_value = CallbackEmulator(self.dist.get_analog_value,
                                                 None,
                                                 self.cb_analog_value,
                                                 self.increase_error_count)

        self.analog_label = AnalogLabel('Analog Value:')
        hlayout = QHBoxLayout()
        self.average_label = QLabel('Moving Average Length:')
        self.average_spin = QSpinBox()
        self.average_spin.setMinimum(1)
        self.average_spin.setMaximum(1000)
        self.average_spin.setSingleStep(1)
        self.average_spin.setValue(25)
        self.average_spin.editingFinished.connect(self.average_spin_finished)

        self.sensor_label = QLabel('Sensor Type:')
        self.sensor_combo = QComboBox()
        self.sensor_combo.addItem('2Y0A41 (4-30cm)')
        self.sensor_combo.addItem('2Y0A21 (10-80cm)')
        self.sensor_combo.addItem('2Y0A02 (20-150cm)')
        self.sensor_combo.currentIndexChanged.connect(self.sensor_combo_changed)

        hlayout.addWidget(self.average_label)
        hlayout.addWidget(self.average_spin)
        hlayout.addStretch()
        hlayout.addWidget(self.sensor_label)
        hlayout.addWidget(self.sensor_combo)

        self.current_distance = CurveValueWrapper() # float, cm

        plots = [('Distance', Qt.red, self.current_distance, '{} cm'.format)]
        self.plot_widget = PlotWidget('Distance [cm]', plots, extra_key_widgets=[self.analog_label], y_resolution=0.1)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def sensor_combo_changed(self, index):
        self.dist.set_sensor_type(index)

    def average_spin_finished(self):
        self.dist.set_moving_average_configuration(self.average_spin.value())

    def get_moving_average_configuration_async(self, average):
        self.average_spin.blockSignals(True)
        self.average_spin.setValue(average)
        self.average_spin.blockSignals(False)

    def get_sensor_type_async(self, sensor):
        self.sensor_combo.blockSignals(True)
        self.sensor_combo.setCurrentIndex(sensor)
        self.sensor_combo.blockSignals(False)

    def start(self):
        async_call(self.dist.get_moving_average_configuration, None, self.get_moving_average_configuration_async, self.increase_error_count)
        async_call(self.dist.get_sensor_type, None, self.get_sensor_type_async, self.increase_error_count)

        self.cbe_distance.set_period(10)
        self.cbe_analog_value.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_distance.set_period(0)
        self.cbe_analog_value.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDistanceIRV2.DEVICE_IDENTIFIER

    def cb_distance(self, distance):
        self.current_distance.value = distance / 10.0

    def cb_analog_value(self, analog_value):
        self.analog_label.setText(analog_value)
