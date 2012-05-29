# -*- coding: utf-8 -*-  
"""
Master Plugin
Copyright (C) 2010 Olaf Lüke <olaf@tinkerforge.com>

master.py: Master Plugin implementation

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

#import logging

from plugin_system.plugin_base import PluginBase
import ip_connection

from PyQt4.QtGui import QWidget, QFrame, QMessageBox
from PyQt4.QtCore import QTimer, Qt

from ui_master import Ui_Master
from ui_chibi import Ui_Chibi
from ui_rs485 import Ui_RS485
from ui_extension_type import Ui_extension_type

import brick_master

class ExtensionTypeWindow(QFrame, Ui_extension_type):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)
        
        self.setWindowTitle("Configure Extension Type")
        
        self.master = parent.master
        self.button_type_save.pressed.connect(self.save_pressed)
        self.combo_extension.currentIndexChanged.connect(self.index_changed)
        
        self.index_changed(0)
        
        
    def popup_ok(self):
        QMessageBox.information(self, "Upload", "Check OK", QMessageBox.Ok)
    
    def popup_fail(self):
        QMessageBox.critical(self, "Upload", "Check Failed", QMessageBox.Ok)
    
    def index_changed(self, index):
        ext = self.master.get_extension_type(index)
        if ext < 0 or ext > 2:
            ext = 0
        self.type_box.setCurrentIndex(ext)
        
    def save_pressed(self):
        extension = self.combo_extension.currentIndex()
        type = self.type_box.currentIndex()
        try:
            self.master.set_extension_type(extension, type)
        except:
            self.popup_fail()
            return
        
        try:
            new_type = self.master.get_extension_type(extension)
        except:
            self.popup_fail()
            return
        
        if type == new_type:
            self.popup_ok()
        else:
            self.popup_fail()
    
class Chibi(QWidget, Ui_Chibi):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.master = parent.master
        
        if parent.version_minor > 0:
            address = self.master.get_chibi_address()
            address_slave = []
            for i in range(32):
                x = self.master.get_chibi_slave_address(i)
                if x == 0:
                    break
                else:
                    address_slave.append(str(x))
                    
            address_slave_text = ', '.join(address_slave)
            address_master = self.master.get_chibi_master_address()
            frequency = self.master.get_chibi_frequency()
            channel = self.master.get_chibi_channel()
            
            type = 0
            if address == address_master:
                type = 1
            
            self.lineedit_slave_address.setText(address_slave_text)
            self.address_spinbox.setValue(address)
            self.master_address_spinbox.setValue(address_master)
            self.chibi_frequency.setCurrentIndex(frequency)
            self.chibi_channel.setCurrentIndex(channel)
            
            self.save_button.pressed.connect(self.save_pressed)
            self.chibi_type.currentIndexChanged.connect(self.chibi_type_changed)
            self.chibi_frequency.currentIndexChanged.connect(self.chibi_frequency_changed)
            self.chibi_channel.currentIndexChanged.connect(self.chibi_channel_changed)
            
            self.chibi_type.setCurrentIndex(type)
            self.chibi_type_changed(type)
            self.new_max_count()
        
    def popup_ok(self):
        QMessageBox.information(self, "Save", "Check OK", QMessageBox.Ok)
    
    def popup_fail(self):
        QMessageBox.critical(self, "Save", "Check Failed", QMessageBox.Ok)
        
    def new_max_count(self):
        channel = int(self.chibi_channel.currentText())
        self.chibi_channel.currentIndexChanged.disconnect(self.chibi_channel_changed)
        
        for i in range(12):
            self.chibi_channel.removeItem(0)
            
        index = self.chibi_frequency.currentIndex()
        
        if index == 0:
            self.chibi_channel.addItem("0")
            if channel != 0:
                channel = 0
        elif index in (1, 3):
            channel -= 1
            self.chibi_channel.addItem("1")
            self.chibi_channel.addItem("2")
            self.chibi_channel.addItem("3")
            self.chibi_channel.addItem("4")
            self.chibi_channel.addItem("5")
            self.chibi_channel.addItem("6")
            self.chibi_channel.addItem("7")
            self.chibi_channel.addItem("8")
            self.chibi_channel.addItem("9")
            self.chibi_channel.addItem("10")
            if not channel in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10):
                channel = 0
        elif index == 2:
            self.chibi_channel.addItem("0")
            self.chibi_channel.addItem("1")
            self.chibi_channel.addItem("2")
            self.chibi_channel.addItem("3")
            if not channel in (0, 1, 2, 3):
                channel = 0
                
                
        self.chibi_channel.setCurrentIndex(channel)
        self.chibi_channel.currentIndexChanged.connect(self.chibi_channel_changed)
            
    def save_pressed(self):
        type = self.chibi_type.currentIndex()
        frequency = self.chibi_frequency.currentIndex()
        channel = self.chibi_channel.currentIndex()
        if frequency in (1, 3):
            channel += 1
        address = self.address_spinbox.value()
        address_master = self.master_address_spinbox.value()
        address_slave_text = str(self.lineedit_slave_address.text().replace(' ', ''))
        if address_slave_text == '':
            address_slave = []
        else:
            address_slave = map(int, address_slave_text.split(','))
            address_slave.append(0)
            
        self.master.set_chibi_frequency(frequency)
        self.master.set_chibi_channel(channel)
        self.master.set_chibi_address(address)
        if type == 0:
            self.master.set_chibi_master_address(address_master)
        else:
            self.master.set_chibi_master_address(address)
            for i in range(len(address_slave)):
                self.master.set_chibi_slave_address(i, address_slave[i])
                
        new_frequency = self.master.get_chibi_frequency()
        new_channel = self.master.get_chibi_channel()
        new_address = self.master.get_chibi_address()
        if type == 0:
            new_address_master = self.master.get_chibi_master_address()
            if new_frequency == frequency and \
               new_channel == channel and \
               new_address == address and \
               new_address_master == address_master:
                self.popup_ok()
            else:
                self.popup_fail()
        else:
            new_address_master = self.master.get_chibi_master_address()
            new_address_slave = []
            for i in range(len(address_slave)):
                new_address_slave.append(self.master.get_chibi_slave_address(i))
            if new_frequency == frequency and \
               new_channel == channel and \
               new_address == address and \
               new_address_master == address and \
               new_address_slave == address_slave:
                self.popup_ok()
            else:
                self.popup_fail()
        
    def index_changed(self, index):
        addr = self.master.get_chibi_slave_address(index)
        self.slave_address_spinbox.setValue(addr)
        
    def chibi_frequency_changed(self, index):
        self.new_max_count()

    def chibi_channel_changed(self, index):
        channel = int(self.chibi_channel.itemText(index))
        
    def chibi_type_changed(self, index):
        if index == 0:
            self.label_slave_address.hide()
            self.lineedit_slave_address.hide()
            self.label_master_address.show()
            self.master_address_spinbox.show()
        else:
            self.label_master_address.hide()
            self.master_address_spinbox.hide()
            self.label_slave_address.show()
            self.lineedit_slave_address.show()
        
    def signal_strength_update(self, ss):
        ss_str = "%g dBm"  % (ss,)
        self.signal_strength_label.setText(ss_str)
        
    def update_data(self):
        try:
            ss = self.master.get_chibi_signal_strength()
            self.signal_strength_update(ss)
        except ip_connection.Error:
            return
    
class RS485(QWidget, Ui_RS485):
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.master = parent.master
        
        if parent.version_minor > 1:
            address = self.master.get_rs485_address()
            address_slave = []
            for i in range(32):
                x = self.master.get_rs485_slave_address(i)
                if x == 0:
                    break
                else:
                    address_slave.append(str(x))
                    
            address_slave_text = ', '.join(address_slave)
            
            type = 0
            if address == 0:
                type = 1
            
            self.lineedit_slave_address.setText(address_slave_text)
            self.address_spinbox.setValue(address)
            
            self.save_button.pressed.connect(self.save_pressed)
            self.rs485_type.currentIndexChanged.connect(self.rs485_type_changed)
            
            self.rs485_type.setCurrentIndex(type)
            self.rs485_type_changed(type)
        
    def popup_ok(self):
        QMessageBox.information(self, "Save", "Check OK", QMessageBox.Ok)
    
    def popup_fail(self):
        QMessageBox.critical(self, "Save", "Check Failed", QMessageBox.Ok)
        
    def save_pressed(self):
        type = self.rs485_type.currentIndex()
        if type == 0:
            address = self.address_spinbox.value()
        else:
            address = 0
            
        address_slave_text = str(self.lineedit_slave_address.text().replace(' ', ''))
        if address_slave_text == '':
            address_slave = []
        else:
            address_slave = map(int, address_slave_text.split(','))
            address_slave.append(0)
            
        self.master.set_rs485_address(address)
        if type == 1:
            for i in range(len(address_slave)):
                self.master.set_rs485_slave_address(i, address_slave[i])
                
        new_address = self.master.get_rs485_address()
        if type == 0:
            if new_address == address:
                self.popup_ok()
            else:
                self.popup_fail()
        else:
            new_address_slave = []
            for i in range(len(address_slave)):
                new_address_slave.append(self.master.get_rs485_slave_address(i))
            if new_address == 0 and new_address_slave == address_slave:
                self.popup_ok()
            else:
                self.popup_fail()
        
    def rs485_type_changed(self, index):
        if index == 0:
            self.label_slave_address.hide()
            self.lineedit_slave_address.hide()
            self.label.show()
            self.address_spinbox.show()
        else:
            self.label_slave_address.show()
            self.lineedit_slave_address.show()
            self.label.hide()
            self.address_spinbox.hide()
            
    def update_data(self):
        pass
        
class Master(PluginBase, Ui_Master):
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        self.setupUi(self)

        self.master = brick_master.Master(self.uid)
        
        self.device = self.master
        self.ipcon.add_device(self.master)
        version = self.master.get_version()
        self.version = '.'.join(map(str, version[1]))
        self.version_minor = version[1][1]
        
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
        self.extensions = []
        num_extensions = 0
        # construct chibi widget
        if self.version_minor > 0:
            self.extension_type_button.pressed.connect(self.extension_pressed)
            if self.master.is_chibi_present():
                num_extensions += 1
                chibi = Chibi(self)
                self.extensions.append(chibi)
                self.extension_layout.addWidget(chibi)
        else:
            self.extension_type_button.setEnabled(False)
            
        # RS485 widget
        if self.version_minor > 1:
            self.extension_type_button.pressed.connect(self.extension_pressed)
            if self.master.is_rs485_present():
                num_extensions += 1
                rs485 = RS485(self)
                self.extensions.append(rs485)
                self.extension_layout.addWidget(rs485)
        else:
            self.extension_type_button.setEnabled(False)
            
        if num_extensions == 0:
            self.extension_label.setText("None Present")
        else:
            self.extension_label.setText("" + str(num_extensions) + " Present")

    def start(self):
        self.update_timer.start(100)

    def stop(self):
        self.update_timer.stop()
    
    @staticmethod
    def has_name(name):
        return 'Master Brick' in name
        
    def update_data(self):
        try:
            sv = self.master.get_stack_voltage()
            sc = self.master.get_stack_current()
            self.stack_voltage_update(sv)
            self.stack_current_update(sc)
        except ip_connection.Error:
            return
        for extension in self.extensions:
            extension.update_data()
        
    def stack_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def stack_current_update(self, sc):
        if sc < 999:
            sc_str = "%gmA" % sc
        else:
            sc_str = "%gA" % round(sc/1000.0, 1)   
        self.stack_current_label.setText(sc_str)
        
    def extension_pressed(self):
        etw = ExtensionTypeWindow(self)
        etw.setAttribute(Qt.WA_QuitOnClose)
        etw.show()
