# -*- coding: utf-8 -*-  
"""
Temperature IR Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

temperature_ir.py: Temperature-IR Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_temperature_ir import BrickletTemperatureIR
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class ObjectLabel(QLabel):
    def setText(self, text):
        text = "Object Temperature: " + text + " %cC" % 0xB0
        super(ObjectLabel, self).setText(text)
        
class AmbientLabel(QLabel):
    def setText(self, text):
        text = "Ambient Temperature: " + text + " %cC" % 0xB0
        super(AmbientLabel, self).setText(text)
    
class TemperatureIR(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletTemperatureIR, *args)
        
        self.tem = self.device

        self.cbe_ambient_temperature = CallbackEmulator(self.tem.get_ambient_temperature,
                                                        self.cb_ambient_temperature,
                                                        self.increase_error_count)
        self.cbe_object_temperature = CallbackEmulator(self.tem.get_object_temperature,
                                                       self.cb_object_temperature,
                                                       self.increase_error_count)

        self.ambient_label = AmbientLabel()
        self.object_label = ObjectLabel()
        
        self.emissivity_label = QLabel('Emissivity: ')
        self.emissivity_edit = QLineEdit()
        self.emissivity_button = QPushButton('Save')
        self.emissivity_layout = QHBoxLayout()
        self.emissivity_layout.addWidget(self.emissivity_label)
        self.emissivity_layout.addWidget(self.emissivity_edit)
        self.emissivity_layout.addWidget(self.emissivity_button)
        
        self.emissivity_button.clicked.connect(self.emissivity_clicked)
        
        self.current_ambient = None
        self.current_object = None
        
        plot_list = [['Ambient', Qt.blue, self.get_current_ambient],
                     ['Object', Qt.red, self.get_current_object]]
        
        self.plot_widget = PlotWidget('Temperature [%cC]' % 0xB0, plot_list)
        
        layout_h1 = QHBoxLayout()
        layout_h1.addStretch()
        layout_h1.addWidget(self.ambient_label)
        layout_h1.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.object_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h1)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)
        layout.addLayout(self.emissivity_layout)
        
    def start(self):
        async_call(self.tem.get_ambient_temperature, None, self.cb_ambient_temperature, self.increase_error_count)
        async_call(self.tem.get_object_temperature, None, self.cb_object_temperature, self.increase_error_count)
        async_call(self.tem.get_emissivity, None, self.cb_emissivity, self.increase_error_count)
        self.cbe_ambient_temperature.set_period(250)
        self.cbe_object_temperature.set_period(250)
        
        self.plot_widget.stop = False
        
    def stop(self):
        self.cbe_ambient_temperature.set_period(0)
        self.cbe_object_temperature.set_period(0)
        
        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'temperature_ir'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletTemperatureIR.DEVICE_IDENTIFIER
    
    def get_current_ambient(self):
        return self.current_ambient
    
    def get_current_object(self):
        return self.current_object

    def cb_object_temperature(self, temperature):
        self.current_object = temperature/10.0
        self.object_label.setText(str(self.current_object))
        
    def cb_ambient_temperature(self, temperature):
        self.current_ambient = temperature/10.0
        self.ambient_label.setText(str(self.current_ambient))
        
    def cb_emissivity(self, emissivity):
        self.emissivity_edit.setText(str(emissivity))
        
    def emissivity_clicked(self):
        value = int(self.emissivity_edit.text())
        try:
            self.tem.set_emissivity(value)
        except ip_connection.Error:
            return
