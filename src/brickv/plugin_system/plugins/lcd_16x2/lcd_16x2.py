# -*- coding: utf-8 -*-  
"""
LCD16x2 Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

humidity.py: LCD16x2 Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox
from PyQt4.QtCore import pyqtSignal
        
from bindings import bricklet_lcd_16x2
from bindings.ks0066u import unicode_to_ks0066u
        
class LCD16x2(PluginBase):
    MAX_LINE = 2
    MAX_POSITION = 16
    qtcb_pressed = pyqtSignal(int)
    qtcb_released = pyqtSignal(int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.lcd = bricklet_lcd_16x2.LCD16x2(self.uid)
        self.ipcon.add_device(self.lcd)
        self.version = '.'.join(map(str, self.lcd.get_version()[1]))
        
        self.qtcb_pressed.connect(self.cb_pressed)
        self.lcd.register_callback(self.lcd.CALLBACK_BUTTON_PRESSED,
                                   self.qtcb_pressed.emit)
        self.qtcb_released.connect(self.cb_released)
        self.lcd.register_callback(self.lcd.CALLBACK_BUTTON_RELEASED,
                                   self.qtcb_released.emit)
        
        self.line_label = QLabel('Line: ')
        self.line_combo = QComboBox()
        for i  in range(LCD16x2.MAX_LINE):
            self.line_combo.addItem(str(i))
        
        self.pos_label = QLabel('Position: ')
        self.pos_combo = QComboBox()
        for i  in range(LCD16x2.MAX_POSITION):
            self.pos_combo.addItem(str(i))
        
        self.pos_layout = QHBoxLayout()
        self.pos_layout.addWidget(self.pos_label)
        self.pos_layout.addWidget(self.pos_combo) 
        self.pos_layout.addStretch()
        
        self.line_layout = QHBoxLayout()
        self.line_layout.addWidget(self.line_label)
        self.line_layout.addWidget(self.line_combo)
        self.line_layout.addStretch()
        
        self.text_label = QLabel('Text: ')
        self.text_edit = QLineEdit();
        self.text_edit.setMaxLength(LCD16x2.MAX_POSITION)
        self.text_button = QPushButton('Send Text')
        self.text_layout = QHBoxLayout()
        self.text_layout.addWidget(self.text_label)
        self.text_layout.addWidget(self.text_edit)
        self.text_layout.addWidget(self.text_button)
        
        self.clear_button = QPushButton("Clear Display")
        
        self.bl_button = QPushButton()
        self.cursor_button = QPushButton()
        self.blink_button = QPushButton()
        
        try:
            if self.lcd.is_backlight_on():
                self.bl_button.setText('Backlight Off')
            else:
                self.bl_button.setText('Backlight On')
                
            cursor, blink = self.lcd.get_config()
            if cursor:
                self.cursor_button.setText('Cursor Off')
            else:
                self.cursor_button.setText('Cursor On')
                
            if blink:
                self.blink_button.setText('Blink Off')
            else:
                self.blink_button.setText('Blink On')
        except ip_connection.Error:
            pass
            
        self.onofflayout = QHBoxLayout()
        self.onofflayout.addWidget(self.bl_button)
        self.onofflayout.addWidget(self.cursor_button)
        self.onofflayout.addWidget(self.blink_button)
            
        self.b0_label = QLabel('Button 0: Released')
        self.b1_label = QLabel('Button 1: Released')
        self.b2_label = QLabel('Button 2: Released')
        
        self.cursor_button.pressed.connect(self.cursor_pressed)
        self.blink_button.pressed.connect(self.blink_pressed)
        self.clear_button.pressed.connect(self.clear_pressed)
        self.bl_button.pressed.connect(self.bl_pressed)
        self.text_button.pressed.connect(self.text_pressed)
        
        layout = QVBoxLayout(self)
        layout.addLayout(self.line_layout)
        layout.addLayout(self.pos_layout)
        layout.addLayout(self.text_layout)
        layout.addWidget(self.clear_button)
        layout.addLayout(self.onofflayout)
        layout.addWidget(self.b0_label)
        layout.addWidget(self.b1_label)
        layout.addWidget(self.b2_label)
        layout.addStretch()

    def start(self):
        pass
        
    def stop(self):
        pass

    @staticmethod
    def has_name(name):
        return 'LCD 16x2 Bricklet' in name 
    
    def cb_pressed(self, button):
        if button == 0:
            self.b0_label.setText('Button 0: Pressed')
        elif button == 1:
            self.b1_label.setText('Button 1: Pressed')
        elif button == 2:
            self.b2_label.setText('Button 2: Pressed')
        
    def cb_released(self, button):
        if button == 0:
            self.b0_label.setText('Button 0: Released')
        elif button == 1:
            self.b1_label.setText('Button 1: Released')
        elif button == 2:
            self.b2_label.setText('Button 2: Released')
    
    def bl_pressed(self):
        try:
            if self.bl_button.text() == 'Backlight On':
                self.lcd.backlight_on()
                self.bl_button.setText('Backlight Off')
            else:
                self.lcd.backlight_off()
                self.bl_button.setText('Backlight On')
        except ip_connection.Error:
            return
    
    def get_config(self):
        cursor = self.cursor_button.text() == 'Cursor Off'
        blink = self.blink_button.text() == 'Blink Off'
        return (cursor, blink)
    
    def cursor_pressed(self):
        cursor, blink = self.get_config()
        try:
            self.lcd.set_config(not cursor, blink)
        except ip_connection.Error:
            return
        
        if cursor:
            self.cursor_button.setText('Cursor On')
        else:
            self.cursor_button.setText('Cursor Off')
    
    def blink_pressed(self):
        cursor, blink = self.get_config()
        try:
            self.lcd.set_config(cursor, not blink)
        except ip_connection.Error:
            return

        if blink:
            self.blink_button.setText('Blink On')
        else:
            self.blink_button.setText('Blink Off')
    
    def clear_pressed(self):
        try:
            self.lcd.clear_display()
        except ip_connection.Error:
            return
    
    def text_pressed(self):
        line = int(self.line_combo.currentText())
        position = int(self.pos_combo.currentText())
        text = unicode(self.text_edit.text().toUtf8(), 'utf-8')
        try:
            self.lcd.write_line(line, position, unicode_to_ks0066u(text))
        except ip_connection.Error:
            return
