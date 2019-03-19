# -*- coding: utf-8 -*-
"""
Accelerometer Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015-2016 Matthias Bolte <matthias@tinkerforge.com>

accelerometer.py: Accelerometer Plugin Implementation

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

import math

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QCheckBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_accelerometer import BrickletAccelerometer
from brickv.plot_widget import PlotWidget, FixedSizeLabel
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class PitchLabel(FixedSizeLabel):
    def setText(self, x, y, z):
        try:
            pitch = int(round(math.atan(x/(math.sqrt(y*y + z*z)))*180/math.pi, 0))
            text = 'Pitch: {}°'.format(pitch)
            super().setText(text)
        except:
            # In case of division by 0 or similar we simply don't update the text
            pass

class RollLabel(FixedSizeLabel):
    def setText(self, x, y, z):
        try:
            roll = int(round(math.atan(y/math.sqrt(x*x+z*z))*180/math.pi, 0))
            text = 'Roll: {}°'.format(roll)
            super().setText(text)
        except:
            # In case of division by 0 or similar we simply don't update the text
            pass

class TemperatureLabel(FixedSizeLabel):
    def setText(self, t):
        text = 'Temperature: {0}°C'.format(t)
        super().setText(text)

class Accelerometer(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAccelerometer, *args)

        self.accelerometer = self.device

        self.cbe_acceleration = CallbackEmulator(self.accelerometer.get_acceleration,
                                                 self.cb_acceleration,
                                                 self.increase_error_count)

        self.cbe_temperature = CallbackEmulator(self.accelerometer.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.current_acceleration = [None, None, None] # float, g

        self.pitch_label = PitchLabel()
        self.roll_label = RollLabel()
        self.temperature_label = TemperatureLabel()

        plots = [('X', Qt.red, lambda: self.current_acceleration[0], '{:.3f} g'.format),
                 ('Y', Qt.darkGreen, lambda: self.current_acceleration[1], '{:.3f} g'.format),
                 ('Z', Qt.blue, lambda: self.current_acceleration[2], '{:.3f} g'.format)]
        self.plot_widget = PlotWidget('Acceleration [g]', plots, extra_key_widgets=[self.pitch_label, self.roll_label, self.temperature_label],
                                      curve_motion_granularity=20, update_interval=0.05)

        self.fs_label = QLabel('Full Scale:')
        self.fs_combo = QComboBox()
        self.fs_combo.addItem("2 g")
        self.fs_combo.addItem("4 g")
        self.fs_combo.addItem("6 g")
        self.fs_combo.addItem("8 g")
        self.fs_combo.addItem("16 g")
        self.fs_combo.currentIndexChanged.connect(self.new_config)

        self.dr_label = QLabel('Data Rate:')
        self.dr_combo = QComboBox()
        self.dr_combo.addItem("Off")
        self.dr_combo.addItem("3.125 Hz")
        self.dr_combo.addItem("6.25 Hz")
        self.dr_combo.addItem("12.5 Hz")
        self.dr_combo.addItem("25 Hz")
        self.dr_combo.addItem("50 Hz")
        self.dr_combo.addItem("100 Hz")
        self.dr_combo.addItem("400 Hz")
        self.dr_combo.addItem("800 Hz")
        self.dr_combo.addItem("1600 Hz")
        self.dr_combo.currentIndexChanged.connect(self.new_config)

        self.fb_label = QLabel('Filter Bandwidth:')
        self.fb_combo = QComboBox()
        self.fb_combo.addItem("800 Hz")
        self.fb_combo.addItem("400 Hz")
        self.fb_combo.addItem("200 Hz")
        self.fb_combo.addItem("50 Hz")
        self.fb_combo.currentIndexChanged.connect(self.new_config)

        self.enable_led = QCheckBox("Enable LED")
        self.enable_led.stateChanged.connect(self.enable_led_changed)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.fs_label)
        hlayout.addWidget(self.fs_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.dr_label)
        hlayout.addWidget(self.dr_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.fb_label)
        hlayout.addWidget(self.fb_combo)
        hlayout.addStretch()
        hlayout.addWidget(self.enable_led)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def enable_led_changed(self, state):
        if state == Qt.Checked:
            self.accelerometer.led_on()
        else:
            self.accelerometer.led_off()

    def is_led_on_async(self, on):
        self.enable_led.setChecked(on)

    def new_config(self):
        dr = self.dr_combo.currentIndex()
        fs = self.fs_combo.currentIndex()
        fb = self.fb_combo.currentIndex()
        self.accelerometer.set_configuration(dr, fs, fb)

    def cb_acceleration(self, data):
        x, y, z = data
        self.current_acceleration = [x / 1000.0, y / 1000.0, z / 1000.0]
        self.pitch_label.setText(x, y, z)
        self.roll_label.setText(x, y, z)

    def get_configuration_async(self, conf):
        self.fs_combo.setCurrentIndex(conf.full_scale)
        self.fb_combo.setCurrentIndex(conf.filter_bandwidth)
        self.dr_combo.setCurrentIndex(conf.data_rate)

    def cb_temperature(self, temp):
        self.temperature_label.setText(temp)

    def start(self):
        async_call(self.accelerometer.is_led_on, None, self.is_led_on_async, self.increase_error_count)
        async_call(self.accelerometer.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.accelerometer.get_acceleration, None, self.cb_acceleration, self.increase_error_count)
        async_call(self.accelerometer.get_temperature, None, self.cb_temperature, self.increase_error_count)
        self.cbe_acceleration.set_period(50)
        self.cbe_temperature.set_period(1000)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_acceleration.set_period(0)
        self.cbe_temperature.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAccelerometer.DEVICE_IDENTIFIER
