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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_pressure import BrickletPressure
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class PressureLabel(QLabel):
    def setText(self, text):
        text = "Pressure: " + text + " kPa"
        super(PressureLabel, self).setText(text)

class Pressure(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletPressure, *args)

        self.p = self.device

        self.cbe_pressure = CallbackEmulator(self.p.get_pressure,
                                             self.cb_pressure,
                                             self.increase_error_count)

        self.pressure_label = PressureLabel('Pressure: ')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Pressure [kPa]', plot_list)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.pressure_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

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

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(QLabel('Sensor Type:'))
        layout_h1.addWidget(self.combo_sensor)
        layout_h1.addStretch()
        layout_h1.addWidget(QLabel('Length of Moving Average:'))
        layout_h1.addWidget(self.spin_average)
        layout.addLayout(layout_h1)

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

    def get_url_part(self):
        return 'pressure'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletPressure.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_pressure(self, pressure):
        p = round(pressure/1000.0, 3)
        self.current_value = p
        self.pressure_label.setText('%.03f' % p)

    def combo_sensor_changed(self):
        self.p.set_sensor_type(self.combo_sensor.currentIndex())

    def spin_average_finished(self):
        self.p.set_moving_average(self.spin_average.value())
