# -*- coding: utf-8 -*-  
"""
Accelerometer Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class AccelerationLabel(QLabel):
    def setText(self, x, y, z):
        text = 'Acceleration X: ' + str(x)
        text += ', Y: ' + str(y)
        text += ', Z: ' + str(z)
        super(AccelerationLabel, self).setText(text)
    
class Accelerometer(PluginBase):
    qtcb_acceleration = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, 'Accelerometer Bricklet', BrickletAccelerometer, *args)

        self.accelerometer = self.device
        
        self.qtcb_acceleration.connect(self.cb_acceleration)
        self.accelerometer.register_callback(self.accelerometer.CALLBACK_ACCELERATION,
                                             self.qtcb_acceleration.emit) 
        
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

    def get_acceleration_async(self, acceleration):
        self.cb_acceleration(*acceleration)

    def cb_acceleration(self, x, y, z):
        self.acceleration_label.setText(x, y, z)
        self.current_acceleration = [x, y, z]
        
    def get_current_x(self):
        return self.current_acceleration[0]

    def get_current_y(self):
        return self.current_acceleration[1]

    def get_current_z(self):
        return self.current_acceleration[2]

    def start(self):
        async_call(self.accelerometer.get_acceleration, None, self.get_acceleration_async, self.increase_error_count)
        async_call(self.accelerometer.set_acceleration_callback_period, 100, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.accelerometer.set_acceleration_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'accelerometer'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAccelerometer.DEVICE_IDENTIFIER
