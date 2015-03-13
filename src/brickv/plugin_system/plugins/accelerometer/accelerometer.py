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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_accelerometer import BrickletAccelerometer
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import Qt

class AccelerationLabel(QLabel):
    def setText(self, x, y, z):
        text = 'Acceleration X: ' + str(x)
        text += ', Y: ' + str(y)
        text += ', Z: ' + str(z)
        super(AccelerationLabel, self).setText(text)
    
class Accelerometer(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletAccelerometer, *args)

        self.accelerometer = self.device

        self.cbe_acceleration = CallbackEmulator(self.accelerometer.get_acceleration,
                                                 self.cb_acceleration,
                                                 self.increase_error_count)

        self.acceleration_label = AccelerationLabel()
        self.current_acceleration = [None, None, None]
        
        plot_list = [['X', Qt.red, self.get_current_x],
                     ['Y', Qt.darkGreen, self.get_current_y],
                     ['Z', Qt.blue, self.get_current_z]]
        self.plot_widget = PlotWidget('Acceleration [G]', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.acceleration_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)

    def cb_acceleration(self, data):
        x, y, z = data
        self.acceleration_label.setText(x, y, z)
        self.current_acceleration = [x, y, z]
        
    def get_current_x(self):
        return self.current_acceleration[0]

    def get_current_y(self):
        return self.current_acceleration[1]

    def get_current_z(self):
        return self.current_acceleration[2]

    def start(self):
        async_call(self.accelerometer.get_acceleration, None, self.cb_acceleration, self.increase_error_count)
        self.cbe_acceleration.set_period(50)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_acceleration.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'accelerometer'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAccelerometer.DEVICE_IDENTIFIER
