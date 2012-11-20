# -*- coding: utf-8 -*-  
"""
Temperature-IR Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

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

from plugin_system.plugin_base import PluginBase
from plot_widget import PlotWidget
from bindings import ip_connection
from bindings.bricklet_temperature_ir import BrickletTemperatureIR

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt4.QtCore import pyqtSignal, Qt

class ObjectLabel(QLabel):
    def setText(self, text):
        text = "Object Temperature: " + text + " %cC" % 0xB0
        super(ObjectLabel, self).setText(text)
        
class AmbientLabel(QLabel):
    def setText(self, text):
        text = "Ambient Temperature: " + text + " %cC" % 0xB0
        super(AmbientLabel, self).setText(text)
    
class TemperatureIR(PluginBase):
    qtcb_ambient_temperature = pyqtSignal(int)
    qtcb_object_temperature = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Temperature IR Bricklet', version)
        
        self.tem = BrickletTemperatureIR(uid, ipcon)
        
        self.qtcb_ambient_temperature.connect(self.cb_ambient_temperature)
        self.tem.register_callback(self.tem.CALLBACK_AMBIENT_TEMPERATURE,
                                   self.qtcb_ambient_temperature.emit)
        self.qtcb_object_temperature.connect(self.cb_object_temperature)
        self.tem.register_callback(self.tem.CALLBACK_OBJECT_TEMPERATURE,
                                   self.qtcb_object_temperature.emit) 
        
        self.ambient_label = AmbientLabel()
        self.object_label = ObjectLabel()
        
        self.emissivity_label = QLabel('Emissivity: ')
        self.emissivity_edit = QLineEdit()
        self.emissivity_button = QPushButton('Save')
        self.emissivity_layout = QHBoxLayout()
        self.emissivity_layout.addWidget(self.emissivity_label)
        self.emissivity_layout.addWidget(self.emissivity_edit)
        self.emissivity_layout.addWidget(self.emissivity_button)
        
        self.emissivity_button.pressed.connect(self.emissivity_pressed)
        
        self.current_ambient = 0
        self.current_object = 0
        
        plot_list = [['amb', Qt.blue, self.get_current_ambient],
                     ['obj', Qt.red, self.get_current_object]]
        
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
        try:
            self.cb_ambient_temperature(self.tem.get_ambient_temperature())
            self.cb_object_temperature(self.tem.get_object_temperature())
            self.emissivity_edit.setText(str(self.tem.get_emissivity()))
            self.tem.set_ambient_temperature_callback_period(250)
            self.tem.set_object_temperature_callback_period(250)
        except ip_connection.Error:
            return
        
        self.plot_widget.stop = False
        
    def stop(self):
        try:
            self.tem.set_ambient_temperature_callback_period(0)
            self.tem.set_object_temperature_callback_period(0)
        except ip_connection.Error:
            pass
        
        self.plot_widget.stop = True

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
        
    def emissivity_pressed(self):
        value = int(self.emissivity_edit.text())
        try:
            self.tem.set_emissivity(value)
        except ip_connection.Error:
            return
