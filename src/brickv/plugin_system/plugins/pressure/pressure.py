# -*- coding: utf-8 -*-
"""
Pressure Plugin
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

pressure.py: Pressure Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_pressure import BrickletPressure
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class Pressure(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletPressure, *args)

        self.p = self.device

        self.cbe_pressure = CallbackEmulator(self.p.get_pressure,
                                             self.cb_pressure,
                                             self.increase_error_count)

        self.current_pressure = None # float, kPa

        plots = [('Pressure', Qt.red, lambda: self.current_pressure, '{:.3f} kPa'.format)]
        self.plot_widget = PlotWidget('Pressure [kPa]', plots, y_resolution=0.001)

        self.combo_sensor = QComboBox()
        self.combo_sensor.addItem('MPX5500')
        self.combo_sensor.addItem('MPXV5004')
        self.combo_sensor.addItem('MPX4115A')
        self.combo_sensor.currentIndexChanged.connect(self.combo_sensor_changed)

        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Sensor Type:'))
        hlayout.addWidget(self.combo_sensor)
        hlayout.addStretch()
        hlayout.addWidget(QLabel('Moving Average Length:'))
        hlayout.addWidget(self.spin_average)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def get_sensor_type_async(self, sensor):
        self.combo_sensor.setCurrentIndex(sensor)

    def get_moving_average_async(self, average):
        self.spin_average.setValue(average)

    def start(self):
        async_call(self.p.get_sensor_type, None, self.get_sensor_type_async, self.increase_error_count)
        async_call(self.p.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.p.get_pressure, None, self.cb_pressure, self.increase_error_count)
        self.cbe_pressure.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_pressure.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPressure.DEVICE_IDENTIFIER

    def cb_pressure(self, pressure):
        self.current_pressure = pressure / 1000.0

    def combo_sensor_changed(self):
        self.p.set_sensor_type(self.combo_sensor.currentIndex())

    def spin_average_finished(self):
        self.p.set_moving_average(self.spin_average.value())
