# -*- coding: utf-8 -*-  
"""
Laser Range Finder Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_laser_range_finder import BrickletLaserRangeFinder
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QSpinBox, QCheckBox, QComboBox

class DistanceLabel(QLabel):
    def setText(self, text):
        text = "Distance: " + str(text) + 'cm'
        super(DistanceLabel, self).setText(text)
        
class VelocityLabel(QLabel):
    def setText(self, text):
        text = "Velocity: " + str(text) + 'm/s'
        super(VelocityLabel, self).setText(text)

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
        
        self.distance_label = DistanceLabel('Distance: ')
        self.velocity_label = VelocityLabel('Velocity: ')

        self.current_distance_value = None
        self.current_velocity_value = None

        plot_list_distance = [['', Qt.red, self.get_current_distance_value]]
        plot_list_velocity = [['', Qt.red, self.get_current_velocity_value]]
        self.plot_widget_distance = PlotWidget('Distance [cm]', plot_list_distance)
        self.plot_widget_velocity = PlotWidget('Velocity [m/s]', plot_list_velocity)

        self.enable_laser = QCheckBox("Enable Laser")
        self.enable_laser.stateChanged.connect(self.enable_laser_changed)

        layout_hel = QHBoxLayout()
        layout_hel.addStretch()
        layout_hel.addWidget(self.enable_laser)
        layout_hel.addStretch()
        
        layout_hld = QHBoxLayout()
        layout_hld.addStretch()
        layout_hld.addWidget(self.distance_label)
        layout_hld.addStretch()
        
        layout_hlv = QHBoxLayout()
        layout_hlv.addStretch()
        layout_hlv.addWidget(self.velocity_label)
        layout_hlv.addStretch()
        
        self.velocity_conf_label = QLabel('Velocity Configuration: ')
        self.velocity_conf_combo = QComboBox()
        self.velocity_conf_combo.addItem("0.10 m/s resolution with max +- 12.70m/s")
        self.velocity_conf_combo.addItem("0.25 m/s resolution with max +- 31.75m/s")
        self.velocity_conf_combo.addItem("0.50 m/s resolution with max +- 63.50m/s")
        self.velocity_conf_combo.addItem("1.00 m/s resolution with max +-127.00m/s")
        self.velocity_conf_combo.activated.connect(self.velocity_conf_changed)
        
        layout_hvc = QHBoxLayout()
        layout_hvc.addStretch()
#        layout_hvc.addWidget(self.velocity_conf_label)
        layout_hvc.addWidget(self.velocity_conf_combo)
        layout_hvc.addStretch()
        
        self.spin_average_distance = QSpinBox()
        self.spin_average_distance.setMinimum(0)
        self.spin_average_distance.setMaximum(50)
        self.spin_average_distance.setSingleStep(1)
        self.spin_average_distance.setValue(10)
        self.spin_average_distance.editingFinished.connect(self.spin_average_finished)
        
        self.spin_average_velocity = QSpinBox()
        self.spin_average_velocity.setMinimum(0)
        self.spin_average_velocity.setMaximum(50)
        self.spin_average_velocity.setSingleStep(1)
        self.spin_average_velocity.setValue(10)
        self.spin_average_velocity.editingFinished.connect(self.spin_average_finished)

        layout_hd = QHBoxLayout()
        layout_hd.addStretch()
        layout_hd.addWidget(QLabel('Length of moving average (Distance):'))
        layout_hd.addWidget(self.spin_average_distance)
        layout_hd.addStretch()

        layout_hv = QHBoxLayout()
        layout_hv.addStretch()
        layout_hv.addWidget(QLabel('Length of moving average (Velocity):'))
        layout_hv.addWidget(self.spin_average_velocity)
        layout_hv.addStretch()
        
        layout_vd = QVBoxLayout()
        layout_vd.addLayout(layout_hld)
        layout_vd.addWidget(self.plot_widget_distance)
        layout_vd.addLayout(layout_hd)
        layout_vd.addStretch()

        layout_vv = QVBoxLayout()
        layout_vv.addLayout(layout_hlv)
        layout_vv.addWidget(self.plot_widget_velocity)
        layout_vv.addLayout(layout_hv)
        layout_vv.addLayout(layout_hvc)
        layout_vv.addStretch()
        
        layout_h2 = QHBoxLayout()
        layout_h2.addLayout(layout_vd)
        layout_h2.addLayout(layout_vv)
        
        layout = QVBoxLayout(self)
        layout.addLayout(layout_hel)
        layout.addLayout(layout_h2)

    def start(self):
        async_call(self.lrf.get_velocity_configuration, None, self.get_velocity_configuration_async, self.increase_error_count)
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
    
    def get_current_distance_value(self):
        return self.current_distance_value

    def get_current_velocity_value(self):
        return self.current_velocity_value
    
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
            
    def velocity_conf_changed(self, value):
        self.lrf.set_velocity_configuration(value)

    def cb_distance(self, distance):
        self.current_distance_value = distance
        self.distance_label.setText(str(distance)) 
        
    def cb_velocity(self, velocity):
        velocity = velocity / 100.0
        self.current_velocity_value = velocity
        self.velocity_label.setText(str(velocity)) 
        
    def get_velocity_configuration_async(self, value):
        self.velocity_conf_combo.setCurrentIndex(value)
        
    def get_moving_average_async(self, avg):
        self.spin_average_distance.setValue(avg.distance_average_length)
        self.spin_average_velocity.setValue(avg.velocity_average_length)
        
    def spin_average_finished(self):
        self.lrf.set_moving_average(self.spin_average_distance.value(), self.spin_average_velocity.value())