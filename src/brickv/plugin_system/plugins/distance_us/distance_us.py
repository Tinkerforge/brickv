# -*- coding: utf-8 -*-  
"""
Distance US Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_distance_us import BrickletDistanceUS
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
        
class DistanceUS(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletDistanceUS, *args)

        self.dist = self.device

        self.cbe_distance = CallbackEmulator(self.dist.get_distance_value,
                                             self.cb_distance,
                                             self.increase_error_count)

        self.current_distance = None

        plots = [('Distance Value', Qt.red, lambda: self.current_distance, str)]
        self.plot_widget = PlotWidget('Distance Value', plots)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.dist.get_distance_value, None, self.cb_distance, self.increase_error_count)
        self.cbe_distance.set_period(100)
            
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_distance.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'distance_us'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDistanceUS.DEVICE_IDENTIFIER

    def cb_distance(self, distance):
        self.current_distance = distance
