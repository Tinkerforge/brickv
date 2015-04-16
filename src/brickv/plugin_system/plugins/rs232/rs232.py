# -*- coding: utf-8 -*-  
"""
RS232 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

rs232.py: RS232 Plugin Implementation

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

import threading

from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QTextCursor
from PyQt4.QtCore import pyqtSignal, Qt

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_rs232 import BrickletRS232
from brickv.plugin_system.plugins.rs232.ui_rs232 import Ui_RS232
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class RS232(PluginBase, Ui_RS232):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRS232, *args)

        self.setupUi(self)
        self.text.setReadOnly(True)
        
        self.rs232 = self.device
        
        #self.cbe_read = CallbackEmulator(self.rs232.read,
        #                                 self.cb_read,
        #                                 self.increase_error_count)
        
        self.input_combobox.addItem("")
        
        self.input_combobox.lineEdit().returnPressed.connect(self.input_changed)
        
        self.baudrate_combobox.activated.connect(self.configuration_changed)
        self.parity_combobox.activated.connect(self.configuration_changed)
        self.stopbits_spinbox.editingFinished.connect(self.configuration_changed)
        self.wordlength_spinbox.editingFinished.connect(self.configuration_changed)
        self.hardware_flowcontrol_combobox.activated.connect(self.configuration_changed)
        self.software_flowcontrol_combobox.activated.connect(self.configuration_changed)
        
        self.save_button.pressed.connect(self.save_pressed)
        self.timer = None

    def read_async(self, r):
        s = ''.join(r.message[:r.length])
        if r.length > 0:
            self.text.moveCursor(QTextCursor.End)
            self.text.insertPlainText(s)
            self.text.moveCursor(QTextCursor.End)
            async_call(self.rs232.read, None, self.read_async, self.increase_error_count)
        else:
            self.timer = threading.Timer(0.1, lambda: async_call(self.rs232.read, None, self.read_async, self.increase_error_count))
            self.timer.start()
            
    def input_return_pressed(self):
        c = ['\0']*60
        
        text = self.input.text() + '\n\r'
        for i, t in enumerate(text):
            c[i] = t
        
        self.rs232.write(c, len(text))
        self.input.setText('')
        
    def input_changed(self):
        text = str(self.input_combobox.currentText()) + '\n\r'
        c = ['\0']*60
        for i, t in enumerate(text):
            c[i] = t
        
        self.rs232.write(c, len(text))

        self.input_combobox.setCurrentIndex(0)
        
    def get_configuration_async(self, conf):
        self.baudrate_combobox.setCurrentIndex(conf.baudrate)
        self.parity_combobox.setCurrentIndex(conf.parity)
        self.stopbits_spinbox.setValue(conf.stopbits)
        self.wordlength_spinbox.setValue(conf.wordlength)
        self.hardware_flowcontrol_combobox.setCurrentIndex(conf.hardware_flowcontrol)
        self.software_flowcontrol_combobox.setCurrentIndex(conf.software_flowcontrol)
        self.save_button.setEnabled(False)
        
    def configuration_changed(self):
        self.save_button.setEnabled(True)
    
    def save_pressed(self):
        baudrate = self.baudrate_combobox.currentIndex()
        parity = self.parity_combobox.currentIndex()
        stopbits = self.stopbits_spinbox.value()
        wordlength = self.wordlength_spinbox.value()
        hardware_flowcontrol = self.hardware_flowcontrol_combobox.currentIndex()
        software_flowcontrol = self.software_flowcontrol_combobox.currentIndex()
        
        self.rs232.set_configuration(baudrate, parity, stopbits, wordlength, hardware_flowcontrol, software_flowcontrol)
        self.save_button.setEnabled(False)
        
    def start(self):
        async_call(self.rs232.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.rs232.read, None, self.read_async, self.increase_error_count)
#        self.cbe_read.set_period(100)
        
    def stop(self):
        pass
#        self.cbe_read.set_period(0)

    def destroy(self):
        pass

    def get_url_part(self):
        return 'rs232'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRS232.DEVICE_IDENTIFIER
