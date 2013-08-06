# -*- coding: utf-8 -*-  
"""
Distance US Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

distance_us.py: Distance US Plugin Implementation

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

from plugin_system.plugin_base import PluginBase
from plot_widget import PlotWidget
from bindings.bricklet_distance_us import BrickletDistanceUS
from async_call import async_call

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout
        
class DistanceLabel(QLabel):
    def setText(self, text):
        text = "Distance: " + text + " cm"
        super(DistanceLabel, self).setText(text)
    
class DistanceUS(PluginBase):
    qtcb_distance = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Distance US Bricklet', version)

        self.dist = BrickletDistanceUS(uid, ipcon)
        
        self.qtcb_distance.connect(self.cb_distance)
        self.dist.register_callback(self.dist.CALLBACK_DISTANCE,
                                    self.qtcb_distance.emit) 
        
        self.distance_label = DistanceLabel('Distance: ')
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Distance [cm]', plot_list)
        
        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.distance_label)
        layout_h1.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addWidget(self.plot_widget)
        layout.addStretch()

    def start(self):
        async_call(self.dist.get_distance, None, self.cb_distance, self.increase_error_count)
        async_call(self.dist.set_distance_callback_period, 100, None, self.increase_error_count)
            
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.dist.set_distance_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def get_url_part(self):
        return 'distance_us'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDistanceUS.DEVICE_IDENTIFIER
    
    def get_current_value(self):
        return self.current_value

    def cb_distance(self, distance):
        self.current_value = distance
        self.distance_label.setText(str(distance)) 
