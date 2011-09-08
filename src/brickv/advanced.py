# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

advanced.py: GUI for advanced features

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

from ui_advanced import Ui_widget_advanced
import time

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QFrame, QFileDialog, QMessageBox

class AdvancedWindow(QFrame, Ui_widget_advanced):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)
        
        self.setWindowTitle("Advanced Functions")
        
        self.ipcon = parent.ipcon
        self.button_name_load.pressed.connect(self.name_load_pressed)
        self.button_name_save.pressed.connect(self.name_save_pressed)
        self.button_uid_load.pressed.connect(self.uid_load_pressed)
        self.button_uid_save.pressed.connect(self.uid_save_pressed)
        self.button_plugin_save.pressed.connect(self.plugin_save_pressed)
        self.button_calibrate.pressed.connect(self.calibrate_pressed)
        self.button_browse.pressed.connect(self.browse_pressed)
        self.combo_brick.currentIndexChanged.connect(self.index_changed)
        self.devices = []
        
        
    def popup_ok(self):
        QMessageBox.information(self, "Upload", "Check OK", QMessageBox.Ok)
    
    def popup_fail(self):
        QMessageBox.critical(self, "Upload", "Check Failed", QMessageBox.Ok)
        pass
        
    def name_save_pressed(self):
        device, port = self.current_device_and_port()
        name = str(self.edit_name.text())
        try:
            self.ipcon.write_bricklet_name(device, port, name)
        except:
            self.popup_fail()
            return
        
        try:
            name_read = self.ipcon.read_bricklet_name(device, port)
        except:
            self.popup_fail()
            return
        
        if name == name_read:
            self.popup_ok()
        else:
            self.popup_fail()
    
    def name_load_pressed(self):
        device, port = self.current_device_and_port()
        name = self.ipcon.read_bricklet_name(device, port)
        self.edit_name.setText(name)
        
    def uid_save_pressed(self):
        device, port = self.current_device_and_port()
        uid = str(self.edit_uid.text())
        try:
            self.ipcon.write_bricklet_uid(device, port, uid)
        except:
            self.popup_fail()
            return
        
        try:
            uid_read = self.ipcon.read_bricklet_uid(device, port)
        except:
            self.popup_fail()
            return
        
        if uid == uid_read:
            self.popup_ok()
        else:
            self.popup_fail()
    
    def uid_load_pressed(self):
        device, port = self.current_device_and_port()
        uid = self.ipcon.read_bricklet_uid(device, port)
        self.edit_uid.setText(uid)
    
    def plugin_save_pressed(self):
        device, port = self.current_device_and_port()
        plugin_url = self.edit_plugin.text()
        plugin = file(plugin_url).read()
        
        try:
            self.ipcon.write_bricklet_plugin(device, port, plugin)
        except:
            self.popup_fail()
            return
        
        time.sleep(2)
        
        try:
            plugin_read = self.ipcon.read_bricklet_plugin(device, 
                                                          port, 
                                                          len(plugin))
        except:
            self.popup_fail()
            return
        
        if plugin == plugin_read:
            self.popup_ok()
        else:
            self.popup_fail()
        
    
    def calibrate_pressed(self):
        self.ipcon.adc_calibrate(self.current_device(), 
                                 str(self.combo_port.currentText()).lower())
        
        self.update_calibration()
    
    def current_device_and_port(self):
        return (self.current_device(), 
                str(self.combo_port.currentText()).lower())
    
    def current_device(self):
        return self.devices[self.combo_brick.currentIndex()]
        
        
    def update_calibration(self, device = None):
        if device == None:
            device = self.current_device()
            
        offset, gain = self.ipcon.get_adc_calibration(device)
        
        self.label_offset.setText(str(offset))
        self.label_gain.setText(str(gain))
        
    def index_changed(self, index):
        if len(self.devices) <= index:
            return
        
        self.update_calibration(self.devices[index])
        
    def browse_pressed(self):
        file_name = QFileDialog.getOpenFileName(self,
                                                "Open Firmware", 
                                                "", 
                                                "*.bin")
        self.edit_plugin.setText(file_name)