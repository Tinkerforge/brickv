# -*- coding: utf-8 -*-  
"""
LCD20x4 Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

lcd_20x4.py: LCD20x4 Plugin Implementation

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
from bindings.bricklet_lcd_20x4 import BrickletLCD20x4
from bindings.ks0066u import unicode_to_ks0066u
from async_call import async_call

from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QGridLayout
from PyQt4.QtCore import pyqtSignal
        
class LCD20x4(PluginBase):
    MAX_LINE = 4
    MAX_POSITION = 20
    qtcb_pressed = pyqtSignal(int)
    qtcb_released = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'LCD 20x4 Bricklet', version)
        
        self.version = version
        self.lcd = BrickletLCD20x4(uid, ipcon)
        
        self.qtcb_pressed.connect(self.cb_pressed)
        self.lcd.register_callback(self.lcd.CALLBACK_BUTTON_PRESSED,
                                   self.qtcb_pressed.emit)
        self.qtcb_released.connect(self.cb_released)
        self.lcd.register_callback(self.lcd.CALLBACK_BUTTON_RELEASED,
                                   self.qtcb_released.emit)
        
        self.line_label = QLabel('Line: ')
        self.line_combo = QComboBox()
        for i  in range(LCD20x4.MAX_LINE):
            self.line_combo.addItem(str(i))
        
        self.pos_label = QLabel('Position: ')
        self.pos_combo = QComboBox()
        for i  in range(LCD20x4.MAX_POSITION):
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
        self.text_edit.setMaxLength(LCD20x4.MAX_POSITION)
        self.text_button = QPushButton('Send Text')
        self.text_layout = QHBoxLayout()
        self.text_layout.addWidget(self.text_label)
        self.text_layout.addWidget(self.text_edit)
        self.text_layout.addWidget(self.text_button)
        
        self.clear_button = QPushButton("Clear Display")
        
        self.bl_button = QPushButton()
        self.cursor_button = QPushButton()
        self.blink_button = QPushButton()
            
        self.onofflayout = QHBoxLayout()
        self.onofflayout.addWidget(self.bl_button)
        self.onofflayout.addWidget(self.cursor_button)
        self.onofflayout.addWidget(self.blink_button)
            
        self.b0_label = QLabel('Button 0: Released,')
        self.b1_label = QLabel('Button 1: Released,')
        self.b2_label = QLabel('Button 2: Released,')
        self.b3_label = QLabel('Button 3: Released')
        
        self.buttonlayout = QHBoxLayout()
        self.buttonlayout.addWidget(self.b0_label)
        self.buttonlayout.addWidget(self.b1_label)
        self.buttonlayout.addWidget(self.b2_label)
        self.buttonlayout.addWidget(self.b3_label)
        
        self.cursor_button.pressed.connect(self.cursor_pressed)
        self.blink_button.pressed.connect(self.blink_pressed)
        self.clear_button.pressed.connect(self.clear_pressed)
        self.bl_button.pressed.connect(self.bl_pressed)
        self.text_button.pressed.connect(self.text_pressed)
        
        if self.version >= (2, 0, 1):
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)
            
            gridlayout = QGridLayout()
            gridlayout.setHorizontalSpacing(0)
            gridlayout.setVerticalSpacing(0)
                    
            self.character_boxes_bool = []
            self.character_boxes = []
            for i in range(5):
                self.character_boxes.append([])
                self.character_boxes_bool.append([])
                for j in range(8):
                    b = QPushButton()
                    b.setAutoFillBackground(True)
                    b.setStyleSheet("background-color: rgb(255, 255, 255)")
                    b.setMaximumSize(25, 25)
                    b.setMinimumSize(25, 25)
                    
                    def get_lambda(i, j):
                        return lambda: self.char_button_pressed(i, j)
                    b.pressed.connect(get_lambda(i, j))
                    
                    self.character_boxes[i].append(b)
                    self.character_boxes_bool[i].append(True)
                    gridlayout.addWidget(b, j, i)
                    
            self.char_index_label = QLabel('Index:')
            self.char_index_combo = QComboBox()
            self.char_index_combo.currentIndexChanged.connect(self.char_index_changed)
            for i in range(8):
                self.char_index_combo.addItem(str(i))
                
            self.char_index_layout = QHBoxLayout()
            self.char_index_layout.addStretch()
            self.char_index_layout.addWidget(self.char_index_label)
            self.char_index_layout.addWidget(self.char_index_combo)
            self.char_index_layout.addStretch()
            
            self.char_index_save = QPushButton('Save Character')
            self.char_index_save.pressed.connect(self.char_index_save_pressed)
            self.char_show = QPushButton('Show all Custom Characters on LCD')
            self.char_show.pressed.connect(self.show_pressed)
            self.char_save_layout = QVBoxLayout()
            self.char_save_layout.addStretch()
            self.char_save_layout.addLayout(self.char_index_layout)
            self.char_save_layout.addWidget(self.char_index_save)
            self.char_save_layout.addWidget(self.char_show)
            self.char_save_layout.addStretch()
            
            
            grid_stretch_layout = QHBoxLayout()
            grid_stretch_layout.addWidget(QLabel('Custom Character: '))
            grid_stretch_layout.addLayout(gridlayout)
            grid_stretch_layout.addLayout(self.char_save_layout)
            grid_stretch_layout.addStretch()
            
            self.char_main_layout = QHBoxLayout()
            self.char_main_layout.addStretch()
            self.char_main_layout.addLayout(grid_stretch_layout)
            self.char_main_layout.addStretch()
            
            self.char_main_layoutv = QVBoxLayout()
            self.char_main_layoutv.addLayout(self.char_main_layout)
            self.char_main_layoutv.addWidget(QLabel('Use "\\0, \\1, ..., \\7" in text field to show custom characters.'))
        
        layout = QVBoxLayout(self)
        layout.addLayout(self.line_layout)
        layout.addLayout(self.pos_layout)
        layout.addLayout(self.text_layout)
        layout.addWidget(self.clear_button)
        layout.addLayout(self.onofflayout)
        layout.addLayout(self.buttonlayout)
        
        if self.version >= (2, 0, 1):
            layout.addWidget(line)
            layout.addLayout(self.char_main_layoutv)
        layout.addStretch()


    def char_button_pressed(self, i, j):
        if self.character_boxes_bool[i][j]:
            self.character_boxes_bool[i][j] = False
            self.character_boxes[i][j].setStyleSheet("background-color: rgb(0, 0, 255)")
        else:
            self.character_boxes_bool[i][j] = True
            self.character_boxes[i][j].setStyleSheet("background-color: rgb(255, 255, 255)")

    def is_backlight_on_async(self, on):
        if on:
            self.bl_button.setText('Backlight Off')
        else:
            self.bl_button.setText('Backlight On')
            
    def get_config_async(self, config):
        cursor, blink = config
        if cursor:
            self.cursor_button.setText('Cursor Off')
        else:
            self.cursor_button.setText('Cursor On')
            
        if blink:
            self.blink_button.setText('Blink Off')
        else:
            self.blink_button.setText('Blink On')

    def start(self):
        async_call(self.lcd.is_backlight_on, None, self.is_backlight_on_async, self.increase_error_count)
        async_call(self.lcd.get_config, None, self.get_config_async, self.increase_error_count)
        
    def stop(self):
        pass

    def get_url_part(self):
        return 'lcd_20x4'
    
    def is_hardware_version_relevant(self, hardware_version):
        if hardware_version <= (1, 1, 0):
            self.b3_label.hide()
        return True

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLCD20x4.DEVICE_IDENTIFIER
    
    def cb_pressed(self, button):
        if button == 0:
            self.b0_label.setText('Button 0: Pressed,')
        elif button == 1:
            self.b1_label.setText('Button 1: Pressed,')
        elif button == 2:
            self.b2_label.setText('Button 2: Pressed,')
        elif button == 3:
            self.b3_label.setText('Button 3: Pressed')
        
    def cb_released(self, button):
        if button == 0:
            self.b0_label.setText('Button 0: Released,')
        elif button == 1:
            self.b1_label.setText('Button 1: Released,')
        elif button == 2:
            self.b2_label.setText('Button 2: Released,')
        elif button == 3:
            self.b3_label.setText('Button 3: Released')
    
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
        if self.version >= (2, 0, 1):
            for i in range(8):
                text = text.replace('\\' + str(i), chr(i+8))
        try:
            self.lcd.write_line(line, position, unicode_to_ks0066u(text)) 
        except ip_connection.Error:
            return
        
    def char_index_save_pressed(self):
        char = [0]*8
        for i in range(len(self.character_boxes)):
            for j in range(len(self.character_boxes[i])):
                if self.character_boxes_bool[i][j]:
                    char[j] |= 1 << (4 - i)
                    
        index = int(self.char_index_combo.currentText())
        self.lcd.set_custom_character(index, char)
        
    def show_pressed(self):
        self.lcd.clear_display()
        line1 = '0:{0} 1:{1} 2:{2} 3:{3}'.format(chr(8), chr(9), chr(10), chr(11))
        line2 = '4:{0} 5:{1} 6:{2} 7:{3}'.format(chr(12), chr(13), chr(14), chr(15))
        self.lcd.write_line(0, 0, line1)
        self.lcd.write_line(1, 0, line2)
    
    def custom_character_async(self, characters):
        for i in range(len(self.character_boxes)):
            for j in range(len(self.character_boxes[i])):
                if characters[j] & (1 << i):
                    self.character_boxes_bool[4-i][j] = True
                    self.character_boxes[4-i][j].setStyleSheet("background-color: rgb(255, 255, 255)")
                else:
                    self.character_boxes_bool[4-i][j] = False
                    self.character_boxes[4-i][j].setStyleSheet("background-color: rgb(0, 0, 255)")
    
    def char_index_changed(self, index):
        async_call(self.lcd.get_custom_character, (index,), self.custom_character_async, self.increase_error_count)
