# -*- coding: utf-8 -*-  
"""
Laser Range Finder Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

laser_range_finder.py: Laser Range Finder Plugin Implementation

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

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, \
                        QFrame, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_laser_range_finder import BrickletLaserRangeFinder
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

def format_distance(distance): # cm
    if distance < 100:
        return str(distance) + ' cm'
    else:
        return '{:.2f} m'.format(round(distance / 100.0, 2))

class LaserRangeFinder(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLaserRangeFinder, *args)

        self.lrf = self.device

        self.cbe_distance = CallbackEmulator(self.lrf.get_distance,
                                             self.cb_distance,
                                             self.increase_error_count)
        self.cbe_velocity = CallbackEmulator(self.lrf.get_velocity,
                                             self.cb_velocity,
                                             self.increase_error_count)

        self.current_distance = None # int, cm
        self.current_velocity = None # float, m/s

        plots_distance = [('Distance', Qt.red, lambda: self.current_distance, format_distance)]
        plots_velocity = [('Velocity', Qt.red, lambda: self.current_velocity, '{:.2f} m/s'.format)]
        self.plot_widget_distance = PlotWidget('Distance [cm]', plots_distance)
        self.plot_widget_velocity = PlotWidget('Velocity [m/s]', plots_velocity)

        self.mode_label = QLabel('Mode: ')
        self.mode_combo = QComboBox()
        self.mode_combo.addItem("Distance: 1cm resolution, 40m max")
        self.mode_combo.addItem("Velocity: 0.10 m/s resolution, 12.70m/s max")
        self.mode_combo.addItem("Velocity: 0.25 m/s resolution, 31.75m/s max")
        self.mode_combo.addItem("Velocity: 0.50 m/s resolution, 63.50m/s max")
        self.mode_combo.addItem("Velocity: 1.00 m/s resolution, 127.00m/s max")
        self.mode_combo.currentIndexChanged.connect(self.mode_changed)

        self.label_average_distance = QLabel('Moving Average Length:')

        self.spin_average_distance = QSpinBox()
        self.spin_average_distance.setMinimum(0)
        self.spin_average_distance.setMaximum(50)
        self.spin_average_distance.setSingleStep(1)
        self.spin_average_distance.setValue(10)
        self.spin_average_distance.editingFinished.connect(self.spin_average_finished)

        self.label_average_velocity = QLabel('Moving Average Length:')

        self.spin_average_velocity = QSpinBox()
        self.spin_average_velocity.setMinimum(0)
        self.spin_average_velocity.setMaximum(50)
        self.spin_average_velocity.setSingleStep(1)
        self.spin_average_velocity.setValue(10)
        self.spin_average_velocity.editingFinished.connect(self.spin_average_finished)

        self.enable_laser = QCheckBox("Enable Laser")
        self.enable_laser.stateChanged.connect(self.enable_laser_changed)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(self.plot_widget_distance)
        layout_h1.addWidget(self.plot_widget_velocity)

        layout_h2 = QHBoxLayout()
        layout_h2.addWidget(self.mode_label)
        layout_h2.addWidget(self.mode_combo)
        layout_h2.addStretch()
        layout_h2.addWidget(self.label_average_distance)
        layout_h2.addWidget(self.spin_average_distance)
        layout_h2.addWidget(self.label_average_velocity)
        layout_h2.addWidget(self.spin_average_velocity)
        layout_h2.addStretch()
        layout_h2.addWidget(self.enable_laser)

        self.widgets_distance = [self.plot_widget_distance, self.spin_average_distance, self.label_average_distance]
        self.widgets_velocity = [self.plot_widget_velocity, self.spin_average_velocity, self.label_average_velocity]

        for w in self.widgets_distance:
            w.hide()
        for w in self.widgets_velocity:
            w.hide()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addWidget(line)
        layout.addLayout(layout_h2)

    def start(self):
        async_call(self.lrf.get_mode, None, self.get_mode_async, self.increase_error_count)
        async_call(self.lrf.is_laser_enabled, None, self.is_laser_enabled_async, self.increase_error_count)
        async_call(self.lrf.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.lrf.get_distance, None, self.cb_distance, self.increase_error_count)
        async_call(self.lrf.get_velocity, None, self.cb_velocity, self.increase_error_count)
        self.cbe_distance.set_period(25)
        self.cbe_velocity.set_period(25)

        self.plot_widget_distance.stop = False
        self.plot_widget_velocity.stop = False
        
    def stop(self):
        self.cbe_distance.set_period(0)
        self.cbe_velocity.set_period(0)
        
        self.plot_widget_distance.stop = True
        self.plot_widget_velocity.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'laser_range_finder'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLaserRangeFinder.DEVICE_IDENTIFIER

    def is_laser_enabled_async(self, enabled):
        if enabled:
            self.enable_laser.setChecked(True)
        else:
            self.enable_laser.setChecked(False)
    
    def enable_laser_changed(self, state):
        if state == Qt.Checked:
            self.lrf.enable_laser()
        else:
            self.lrf.disable_laser()
            
    def mode_changed(self, value):
        self.lrf.set_mode(value)
        if value == 0:
            for w in self.widgets_velocity:
                w.hide()
            for w in self.widgets_distance:
                w.show()
        else:
            for w in self.widgets_distance:
                w.hide()
            for w in self.widgets_velocity:
                w.show()

    def cb_distance(self, distance):
        self.current_distance = distance

    def cb_velocity(self, velocity):
        self.current_velocity = velocity / 100.0

    def get_mode_async(self, value):
        self.mode_combo.setCurrentIndex(value)
        self.mode_changed(value)
        
    def get_moving_average_async(self, avg):
        self.spin_average_distance.setValue(avg.distance_average_length)
        self.spin_average_velocity.setValue(avg.velocity_average_length)
        
    def spin_average_finished(self):
        self.lrf.set_moving_average(self.spin_average_distance.value(), self.spin_average_velocity.value())
