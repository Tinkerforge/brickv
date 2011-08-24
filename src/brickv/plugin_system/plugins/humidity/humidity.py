# -*- coding: utf-8 -*-  
"""
Humidity Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

humidity.py: Humidity Plugin Implementation

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

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt
        
import bricklet_humidity
        
class HumidityLabel(QLabel):
    def setText(self, text):
        text = "Humidity: " + text + " %RH (Relative Humidity)"
        super(HumidityLabel, self).setText(text)
    
class Humidity(PluginBase):
    qtcb_humidity = pyqtSignal(int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.hum = bricklet_humidity.Humidity(self.uid)
        self.ipcon.add_device(self.hum)
        
        self.qtcb_humidity.connect(self.cb_humidity)
        self.hum.register_callback(self.hum.CALLBACK_HUMIDITY,
                                   self.qtcb_humidity.emit) 
        
        self.humidity_label = HumidityLabel('Humidity: ')
        
        self.current_value = 0
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Relative Humidity [%RH]', plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.humidity_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)

    def start(self):
        self.cb_humidity(self.hum.get_humidity())
        self.hum.set_humidity_callback_period(100)
        self.plot_widget.stop = False
        
    def stop(self):
        self.hum.set_humidity_callback_period(0)
        self.plot_widget.stop = True

    @staticmethod
    def has_name(name):
        return 'Humidity Bricklet' in name 
    
    def get_current_value(self):
        return self.current_value

    def cb_humidity(self, humidity):
        self.current_value = humidity/10.0
        self.humidity_label.setText(str(humidity/10.0)) 