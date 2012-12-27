# -*- coding: utf-8 -*-  
"""
Temperature Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

temperature.py: Temperature Plugin Implementation

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
from bindings import ip_connection
from bindings.bricklet_temperature import BrickletTemperature
from async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout
from PyQt4.QtCore import pyqtSignal, Qt

class TemperatureLabel(QLabel):
    def setText(self, text):
        text = "Temperature: " + text + " %cC" % 0xB0
        super(TemperatureLabel, self).setText(text)
    
class Temperature(PluginBase):
    qtcb_temperature = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Temperature Bricklet', version)
        
        self.tem = BrickletTemperature(uid, ipcon)
        
        self.qtcb_temperature.connect(self.cb_temperature)
        self.tem.register_callback(self.tem.CALLBACK_TEMPERATURE,
                                   self.qtcb_temperature.emit) 
        
        self.temperature_label = TemperatureLabel()
        
        self.current_value = None
        
        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Temperature [%cC]' % 0xB0, plot_list)
        
        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.temperature_label)
        layout_h.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.tem.get_temperature, None, self.cb_temperature, self.increase_error_count)
        async_call(self.tem.set_temperature_callback_period, 100, None, self.increase_error_count)
        
        self.plot_widget.stop = False
        
    def stop(self):
        async_call(self.tem.set_temperature_callback_period, 0, None, self.increase_error_count)
        
        self.plot_widget.stop = True

    def get_url_part(self):
        return 'temperature'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTemperature.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_temperature(self, temperature):
        self.current_value = temperature/100.0
        self.temperature_label.setText(str(temperature/100.0))
