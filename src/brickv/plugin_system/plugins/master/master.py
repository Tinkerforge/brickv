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
    def __init__(self, master):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.master = master
        
        address = self.master.get_chibi_address()
        address_recv = self.master.get_chibi_receiver_address(0)
        
        self.address_box.setValue(address)
        self.receiver_address_box.setValue(address_recv)
        
        self.receiver_num_combo.currentIndexChanged.connect(self.index_changed)
        self.address_button.pressed.connect(self.address_pressed)
        self.receiver_address_button.pressed.connect(self.receiver_address_pressed)
        
    def popup_ok(self):
        QMessageBox.information(self, "Save", "Check OK", QMessageBox.Ok)
    
    def popup_fail(self):
        QMessageBox.critical(self, "Save", "Check Failed", QMessageBox.Ok)
        
    def address_pressed(self):
        addr = self.address_box.value()
        try:
            self.master.set_chibi_address(addr)
        except:
            self.popup_fail()
            return
        
        try:
            new_addr = self.master.get_chibi_address()
        except:
            self.popup_fail()
            return
        
        if addr == new_addr:
            self.popup_ok()
        else:
            self.popup_fail()
        
    def receiver_address_pressed(self):
        num = self.receiver_num_combo.currentIndex()
        addr = self.receiver_address_box.value()
        try:
            self.master.set_chibi_receiver_address(num, addr)
        except:
            self.popup_fail()
            return
        
        try:
            new_addr = self.master.get_chibi_receiver_address(num)
        except:
            self.popup_fail()
            return
        
        if addr == new_addr:
            self.popup_ok()
        else:
            self.popup_fail()
        
    def index_changed(self, index):
        addr = self.master.get_chibi_receiver_address(index)
        self.receiver_address_box.setValue(addr)
    

class Master(PluginBase, Ui_Master):
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        self.setupUi(self)

        self.master = brick_master.Master(self.uid)
        self.device = self.master
        self.ipcon.add_device(self.master)
        self.version = '.'.join(map(str, self.master.get_version()[1]))
        
        self.extension_type_button.pressed.connect(self.extension_pressed)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        
        num_extensions = 0
        # construct chibi widget
        if self.master.is_chibi_present():
            num_extensions += 1
            chibi = Chibi(self.master)
            self.extension_layout.addWidget(chibi)
            
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