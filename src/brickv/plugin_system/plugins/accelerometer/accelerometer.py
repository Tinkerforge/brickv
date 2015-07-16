# -*- coding: utf-8 -*-  
"""
Accelerometer Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QCheckBox, QFont

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_accelerometer import BrickletAccelerometer
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MonoSpaceLabel(QLabel):
    def __init__(self):
        super(MonoSpaceLabel, self).__init__()

        font = QFont('monospace')
        font.setStyleHint(QFont.TypeWriter)

        self.setFont(font)

class PitchRollLabel(MonoSpaceLabel):
    def setText(self, x, y, z):
        try:
            text = u'Pitch: {0:+03d}°'.format(int(round(math.atan(x/(math.sqrt(y*y + z*z)))*180/math.pi, 0)))
            text += u', Roll: {0:+03d}°'.format(int(round(math.atan(y/math.sqrt(x*x+z*z))*180/math.pi, 0)))
            text = text.replace('-0', '- ')
            text = text.replace('+0', '+ ')
            super(PitchRollLabel, self).setText(text)
        except:
            # In case of division by 0 or similar we simply don't update the text
            pass

class TemperatureLabel(MonoSpaceLabel):
    def setText(self, t):
        text = u'Temperature: {0}°C'.format(t)
        super(TemperatureLabel, self).setText(text)

class AccelerationLabel(MonoSpaceLabel):
    def setText(self, x, y, z):
        text = u'Acceleration X: {0:+.3f}g'.format(round(x/1000.0, 3))
        text += u', Y: {0:+.3f}g'.format(round(y/1000.0, 3))
        text += u', Z: {0:+.3f}g'.format(round(z/1000.0, 3))
        super(AccelerationLabel, self).setText(text)
    
class Accelerometer(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletAccelerometer, *args)

        self.accelerometer = self.device

        self.cbe_acceleration = CallbackEmulator(self.accelerometer.get_acceleration,
                                                 self.cb_acceleration,
                                                 self.increase_error_count)
        
        self.cbe_temperature = CallbackEmulator(self.accelerometer.get_temperature,
                                                self.cb_temperature,
                                                self.increase_error_count)

        self.acceleration_label = AccelerationLabel()
        self.current_acceleration = [None, None, None]
        
        plot_list = [['X', Qt.red, self.get_current_x],
                     ['Y', Qt.darkGreen, self.get_current_y],
                     ['Z', Qt.blue, self.get_current_z]]
        self.plot_widget = PlotWidget('Acceleration [g]', plot_list)
        
        self.temperature_label = TemperatureLabel()
        layout_ht = QHBoxLayout()
        layout_ht.addStretch()
        layout_ht.addWidget(self.temperature_label)
        layout_ht.addStretch()
        
        self.pitch_roll_label = PitchRollLabel()
        layout_hpr = QHBoxLayout()
        layout_hpr.addStretch()
        layout_hpr.addWidget(self.pitch_roll_label)
        layout_hpr.addStretch()
        
        self.enable_led = QCheckBox("LED On")
        self.enable_led.stateChanged.connect(self.enable_led_changed)
        
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
        
        layout_hc = QHBoxLayout()
        layout_hc.addStretch()
        layout_hc.addWidget(self.fs_label)
        layout_hc.addWidget(self.fs_combo)
        layout_hc.addStretch()
        layout_hc.addWidget(self.dr_label)
        layout_hc.addWidget(self.dr_combo)
        layout_hc.addStretch()
        layout_hc.addWidget(self.fb_label)
        layout_hc.addWidget(self.fb_combo)
        layout_hc.addStretch()
        layout_hc.addWidget(self.enable_led)
        layout_hc.addStretch()

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.acceleration_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_ht)
        layout.addLayout(layout_hpr)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)
        layout.addLayout(layout_hc)
        
    def enable_led_changed(self, state):
        if state == Qt.Checked:
            self.accelerometer.led_on()
        else:
            self.accelerometer.led_off()
        
    def is_led_on_async(self, value):
        if value:
            self.enable_led.setChecked(True)
        else:
            self.enable_led.setChecked(False)
        
    def new_config(self):
        dr = self.dr_combo.currentIndex()
        fs = self.fs_combo.currentIndex()
        fb = self.fb_combo.currentIndex()
        self.accelerometer.set_configuration(dr, fs, fb)

    def cb_acceleration(self, data):
        x, y, z = data
        self.acceleration_label.setText(x, y, z)
        self.pitch_roll_label.setText(x, y, z)
        self.current_acceleration = [x/1000.0, y/1000.0, z/1000.0]
        
    def cb_configuration(self, conf):
        self.fs_combo.setCurrentIndex(conf.full_scale)
        self.fb_combo.setCurrentIndex(conf.filter_bandwidth)
        self.dr_combo.setCurrentIndex(conf.data_rate)
        
    def cb_temperature(self, temp):
        self.temperature_label.setText(temp)
        
    def get_current_x(self):
        return self.current_acceleration[0]

    def get_current_y(self):
        return self.current_acceleration[1]

    def get_current_z(self):
        return self.current_acceleration[2]

    def start(self):
        async_call(self.accelerometer.is_led_on, None, self.is_led_on_async, self.increase_error_count)
        async_call(self.accelerometer.get_configuration, None, self.cb_configuration, self.increase_error_count)
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

    def get_url_part(self):
        return 'accelerometer'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAccelerometer.DEVICE_IDENTIFIER
