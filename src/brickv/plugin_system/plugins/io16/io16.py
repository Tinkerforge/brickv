# -*- coding: utf-8 -*-  
"""
IO-16 Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

io16.py: IO-16 Plugin Implementation

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
import ip_connection
from PyQt4.QtCore import pyqtSignal
from ui_io16 import Ui_IO16

import bricklet_io16
        
class IO16(PluginBase, Ui_IO16):
    qtcb_interrupt = pyqtSignal('char', int, int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.io = bricklet_io16.IO16(self.uid)
        self.ipcon.add_device(self.io)
        self.version = '.'.join(map(str, self.io.get_version()[1]))
        
        self.qtcb_interrupt.connect(self.cb_interrupt)
        self.io.register_callback(self.io.CALLBACK_INTERRUPT,
                                  self.qtcb_interrupt.emit)
        
        self.port_value = { 'a': [self.av0, self.av1, self.av2, self.av3,
                                  self.av4, self.av5, self.av6, self.av7],
                            'b': [self.bv0, self.bv1, self.bv2, self.bv3,
                                  self.bv4, self.bv5, self.bv6, self.bv7]}
        
        self.port_direction = { 'a': [self.ad0, self.ad1, self.ad2, self.ad3,
                                      self.ad4, self.ad5, self.ad6, self.ad7],
                                'b': [self.bd0, self.bd1, self.bd2, self.bd3,
                                      self.bd4, self.bd5, self.bd6, self.bd7]}
        
        self.port_config = { 'a': [self.ac0, self.ac1, self.ac2, self.ac3,
                                   self.ac4, self.ac5, self.ac6, self.ac7],
                             'b': [self.bc0, self.bc1, self.bc2, self.bc3,
                                   self.bc4, self.bc5, self.bc6, self.bc7]}
        
        try:
            value = self.io.get_port('a')
            dir, config = self.io.get_port_configuration('a')
            self.init_values('a', value, dir, config)
        
            value = self.io.get_port('b')
            dir, config = self.io.get_port_configuration('b')
            self.init_values('b', value, dir, config)
        
            debounce = self.io.get_debounce_period()
            self.debounce_edit.setText(str(debounce))
        except ip_connection.Error:
            pass
        
        self.save_button.pressed.connect(self.save_pressed)
        self.port_box.currentIndexChanged.connect(self.port_changed)
        self.pin_box.currentIndexChanged.connect(self.pin_changed)
        self.direction_box.currentIndexChanged.connect(self.direction_changed)
        self.debounce_save.pressed.connect(self.debounce_save_pressed)
        
        self.port_changed(0)
        
    def start(self):
        try:
            self.io.set_port_interrupt('a', 0xFF)
            self.io.set_port_interrupt('b', 0xFF)
        except ip_connection.Error:
            return
        
    def stop(self):
        try:
            self.io.set_port_interrupt('a', 0)
            self.io.set_port_interrupt('b', 0)
        except ip_connection.Error:
            return

    @staticmethod
    def has_name(name):
        return 'IO-16 Bricklet' in name 
    
    def init_values(self, port, value, dir, config):
        for i in range(8):
            if dir & (1 << i):
                self.port_direction[port][i].setText('Input')
                
                if config & (1 << i):
                    self.port_config[port][i].setText('Pull Up')
                else:
                    self.port_config[port][i].setText('Default')
            else:
                self.port_direction[port][i].setText('Output')
                
                if config & (1 << i):
                    self.port_config[port][i].setText('High')
                else:
                    self.port_config[port][i].setText('Low')
            
            if value & (1 << i):
                self.port_value[port][i].setText('High')
            else:
                self.port_value[port][i].setText('Low')
                
    def save_pressed(self):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())
        direction = str(self.direction_box.currentText())[0].lower()
        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[port][pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull Up'
            
        try:
            self.io.set_port_configuration(port, 1 << pin, direction, value)
        except ip_connection.Error:
            return
            
        self.port_direction[port][pin].setText(self.direction_box.currentText())
        self.port_config[port][pin].setText(self.value_box.currentText())
        
    def cb_interrupt(self, port, interrupt, value):
        for i in range(8):
            if interrupt & (1 << i):
                if value & (1 << i):
                    self.port_value[port][i].setText('High')
                else:
                    self.port_value[port][i].setText('Low')
    
    def port_changed(self, port):
        self.pin_changed(int(self.pin_box.currentText()))
                    
    def pin_changed(self, pin):
        port = str(self.port_box.currentText()).lower()
        
        if str(self.port_direction[port][pin].text()) == 'Input':
            index = 0
        else:
            index = 1
            
        self.direction_box.setCurrentIndex(index)
        self.direction_changed(index)
        
    def direction_changed(self, direction):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())
        
        while self.value_box.count() != 0:
            self.value_box.removeItem(0)
            
        if direction == 1:
            self.value_box.addItem('High')
            self.value_box.addItem('Low')
            if str(self.port_config[port][pin].text()) == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_box.addItem('Pull Up')
            self.value_box.addItem('Default')
            if str(self.port_config[port][pin].text()) == 'Pull Up':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
                
    def debounce_save_pressed(self):
        debounce = int(str(self.debounce_edit.text()))
        try:
            self.io.set_debounce_period(debounce)
        except ip_connection.Error:
            return
            