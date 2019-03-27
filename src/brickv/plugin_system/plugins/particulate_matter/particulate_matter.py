# -*- coding: utf-8 -*-
"""
Particulate Matter Plugin
Copyright (C) 2018 Matthias Bolte <matthias@tinkerforge.com>

particulate_matter.py: Particulate Matter Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox, QLabel

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_particulate_matter import BrickletParticulateMatter
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class ParticulateMatter(COMCUPluginBase):
    def __init__(self, *args):
        super().__init__(BrickletParticulateMatter, *args)

        self.pm = self.device

        self.cbe_pm_concentration = CallbackEmulator(self.pm.get_pm_concentration,
                                                     self.cb_pm_concentration,
                                                     self.increase_error_count)

        self.cbe_pm_count = CallbackEmulator(self.pm.get_pm_count,
                                             self.cb_pm_count,
                                             self.increase_error_count)

        self.current_pm_concentration_pm10 = CurveValueWrapper()
        self.current_pm_concentration_pm25 = CurveValueWrapper()
        self.current_pm_concentration_pm100 = CurveValueWrapper()

        plots = [('PM1.0', Qt.red, self.current_pm_concentration_pm10, '{} µg/m³'.format),
                 ('PM2.5', Qt.darkGreen, self.current_pm_concentration_pm25, '{} µg/m³'.format),
                 ('PM10.0', Qt.blue, self.current_pm_concentration_pm100, '{} µg/m³'.format)]
        self.plot_widget = PlotWidget('PM Concentration [µg/m³]', plots, y_resolution=1.0)

        self.label_count = QLabel('PM Count > 0.3, 0.5, 1.0, 2.5, 5.0, 10.0 µm:')
        self.label_count_value = QLabel('0, 0, 0, 0, 0, 0')

        self.check_enable_sensor = QCheckBox('Enable Sensor')
        self.check_enable_sensor.stateChanged.connect(self.enable_sensor_changed)

        self.label_sensor_version = QLabel('Sensor Version:')
        self.label_sensor_version_value = QLabel('0')

        self.label_last_error_code = QLabel('Last Error Code:')
        self.label_last_error_code_value = QLabel('0')

        self.label_framing_errors = QLabel('Framing Errors:')
        self.label_framing_errors_value = QLabel('0')

        self.label_checksum_errors = QLabel('Checksum Errors:')
        self.label_checksum_errors_value = QLabel('0')

        layout_sub1 = QHBoxLayout()
        layout_sub1.addWidget(self.label_count)
        layout_sub1.addWidget(self.label_count_value)
        layout_sub1.addStretch()
        layout_sub1.addWidget(self.check_enable_sensor)

        layout_sub2 = QHBoxLayout()
        layout_sub2.addWidget(self.label_sensor_version)
        layout_sub2.addWidget(self.label_sensor_version_value)
        layout_sub2.addStretch()
        layout_sub2.addWidget(self.label_last_error_code)
        layout_sub2.addWidget(self.label_last_error_code_value)
        layout_sub2.addStretch()
        layout_sub2.addWidget(self.label_framing_errors)
        layout_sub2.addWidget(self.label_framing_errors_value)
        layout_sub2.addStretch()
        layout_sub2.addWidget(self.label_checksum_errors)
        layout_sub2.addWidget(self.label_checksum_errors_value)

        layout_main = QVBoxLayout(self)
        layout_main.addWidget(self.plot_widget)
        layout_main.addLayout(layout_sub1)
        layout_main.addLayout(layout_sub2)

        self.sensor_info_timer = QTimer(self)
        self.sensor_info_timer.timeout.connect(self.update_sensor_info)
        self.sensor_info_timer.setInterval(1000)

    def enable_sensor_changed(self, state):
        self.pm.set_enable(state == Qt.Checked)

    def start(self):
        async_call(self.pm.get_pm_concentration, None, self.cb_pm_concentration, self.increase_error_count)
        async_call(self.pm.get_pm_count, None, self.cb_pm_count, self.increase_error_count)
        async_call(self.pm.get_enable, None, self.get_enable_async, self.increase_error_count)

        self.cbe_pm_concentration.set_period(100)
        self.cbe_pm_count.set_period(100)

        self.plot_widget.stop = False

        self.update_sensor_info()
        self.sensor_info_timer.start()

    def stop(self):
        self.sensor_info_timer.stop()

        self.cbe_pm_concentration.set_period(0)
        self.cbe_pm_count.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletParticulateMatter.DEVICE_IDENTIFIER

    def cb_pm_concentration(self, pm_concentration):
        self.current_pm_concentration_pm10.value = pm_concentration.pm10
        self.current_pm_concentration_pm25.value = pm_concentration.pm25
        self.current_pm_concentration_pm100.value = pm_concentration.pm100

    def cb_pm_count(self, pm_count):
        self.label_count_value.setText(', '.join(map(str, pm_count)))

    def get_enable_async(self, enable):
        self.check_enable_sensor.setChecked(enable)

    def update_sensor_info(self):
        async_call(self.pm.get_sensor_info, None, self.get_sensor_info_async, self.increase_error_count)

    def get_sensor_info_async(self, info):
        self.label_sensor_version_value.setText(str(info.sensor_version))
        self.label_last_error_code_value.setText(str(info.last_error_code))
        self.label_framing_errors_value.setText(str(info.framing_error_count))
        self.label_checksum_errors_value.setText(str(info.checksum_error_count))
