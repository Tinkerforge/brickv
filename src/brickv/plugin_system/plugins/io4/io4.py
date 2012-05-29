# -*- coding: utf-8 -*-  
"""
IO4 Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

humidity.py: IO4 Plugin Implementation

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
from bindings import ip_connection
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import pyqtSignal
from ui_io4 import Ui_IO4

from bindings import bricklet_io4
        
class IO4(PluginBase, Ui_IO4):
    qtcb_interrupt = pyqtSignal(int, int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.io = bricklet_io4.IO4(self.uid)
        self.ipcon.add_device(self.io)
        self.version = '.'.join(map(str, self.io.get_version()[1]))
        
        self.qtcb_interrupt.connect(self.cb_interrupt)
        self.io.register_callback(self.io.CALLBACK_INTERRUPT,
                                  self.qtcb_interrupt.emit)
        
        self.port_value = [self.av0, self.av1, self.av2, self.av3]
        self.port_direction = [self.ad0, self.ad1, self.ad2, self.ad3]
        self.port_config = [self.ac0, self.ac1, self.ac2, self.ac3]
        
        try:
            value = self.io.get_value()
            dir, config = self.io.get_configuration()
            self.init_values(value, dir, config)
        
            debounce = self.io.get_debounce_period()
            self.debounce_edit.setText(str(debounce))
        except ip_connection.Error:
            pass
        
        self.save_button.pressed.connect(self.save_pressed)
        self.pin_box.currentIndexChanged.connect(self.pin_changed)
        self.direction_box.currentIndexChanged.connect(self.direction_changed)
        self.debounce_save.pressed.connect(self.debounce_save_pressed)
        
        self.pin_changed(0)
        
    def start(self):
        try:
            self.io.set_interrupt(1 | 2 | 4 | 8)
        except ip_connection.Error:
            return
        
    def stop(self):
        try:
            self.io.set_interrupt(0)
        except ip_connection.Error:
            return

    @staticmethod
    def has_name(name):
        return 'IO-4 Bricklet' in name 
    
    def init_values(self, value, dir, config):
        for i in range(4):
            if dir & (1 << i):
                self.port_direction[i].setText('Input')
                
                if config & (1 << i):
                    self.port_config[i].setText('Pull Up')
                else:
                    self.port_config[i].setText('Default')
            else:
                self.port_direction[i].setText('Output')
                
                if config & (1 << i):
                    self.port_config[i].setText('High')
                else:
                    self.port_config[i].setText('Low')
            
            if value & (1 << i):
                self.port_value[i].setText('High')
            else:
                self.port_value[i].setText('Low')
                
    def save_pressed(self):
        pin = int(self.pin_box.currentText())
        direction = str(self.direction_box.currentText())[0].lower()
        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull Up'
            
        try:
            self.io.set_configuration(1 << pin, direction, value)
        except ip_connection.Error:
            return
            
        self.port_direction[pin].setText(self.direction_box.currentText())
        self.port_config[pin].setText(self.value_box.currentText())
        
    def cb_interrupt(self, interrupt, value):
        for i in range(4):
            if interrupt & (1 << i):
                if value & (1 << i):
                    self.port_value[i].setText('High')
                else:
                    self.port_value[i].setText('Low')
    
    def pin_changed(self, pin):
        if str(self.port_direction[pin].text()) == 'Input':
            index = 0
        else:
            index = 1
            
        self.direction_box.setCurrentIndex(index)
        self.direction_changed(index)
        
    def direction_changed(self, direction):
        pin = int(self.pin_box.currentText())
        
        while self.value_box.count() != 0:
            self.value_box.removeItem(0)
            
        if direction == 1:
            self.value_box.addItem('High')
            self.value_box.addItem('Low')
            if str(self.port_config[pin].text()) == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_box.addItem('Pull Up')
            self.value_box.addItem('Default')
            if str(self.port_config[pin].text()) == 'Pull Up':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
                
    def debounce_save_pressed(self):
        debounce = int(str(self.debounce_edit.text()))
        try:
            self.io.set_debounce_period(debounce)
        except ip_connection.Error:
            return
            