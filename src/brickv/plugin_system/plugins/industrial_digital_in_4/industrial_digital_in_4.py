# -*- coding: utf-8 -*-  
"""
Industrial Digital In 4 Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

industrial_digital_in_4.py: Industrial Digital In 4 Plugin Implementation

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
from PyQt4.QtCore import Qt, pyqtSignal
from async_call import async_call

from ui_industrial_digital_in_4 import Ui_IndustrialDigitalIn4
from dio_gnd_pixmap import get_dio_gnd_pixmap
from dio_vcc_pixmap import get_dio_vcc_pixmap

from bindings.bricklet_industrial_digital_in_4 import BrickletIndustrialDigitalIn4
        
class IndustrialDigitalIn4(PluginBase, Ui_IndustrialDigitalIn4):
    qtcb_interrupt = pyqtSignal(int, int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Industrial Digital In 4 Bricklet', version)
        
        self.setupUi(self)
        
        self.idi4 = BrickletIndustrialDigitalIn4(uid, ipcon)
        
        self.gnd_pixmap = get_dio_gnd_pixmap()
        self.vcc_pixmap = get_dio_vcc_pixmap()
        
        self.pin_buttons = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b10, self.b11, self.b12, self.b13, self.b14, self.b15]
        self.pin_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon, self.b4_icon, self.b5_icon, self.b6_icon, self.b7_icon, self.b8_icon, self.b9_icon, self.b10_icon, self.b11_icon, self.b12_icon, self.b13_icon, self.b14_icon, self.b15_icon]
        self.pin_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label, self.b4_label, self.b5_label, self.b6_label, self.b7_label, self.b8_label, self.b9_label, self.b10_label, self.b11_label, self.b12_label, self.b13_label, self.b14_label, self.b15_label]
        self.groups = [self.group0, self.group1, self.group2, self.group3]
            
        self.line_1vs2.setVisible(False)
        self.line_2vs3.setVisible(False)
        self.line_3vs4.setVisible(False)
        
        self.available_ports = 0
        async_call(self.idi4.get_available_for_group, None, self.get_available_for_group_aysnc, self.increase_error_count)
        
        self.qtcb_interrupt.connect(self.cb_interrupt)
        self.idi4.register_callback(self.idi4.CALLBACK_INTERRUPT,
                                    self.qtcb_interrupt.emit)
        
        self.set_group.pressed.connect(self.set_group_pressed)
        
        self.debounce_go.pressed.connect(self.debounce_go_pressed)
        
        self.reconfigure_everything()
        
    def get_available_for_group_aysnc(self, available_ports):
        self.available_ports = available_ports
        
    def start(self):
        async_call(self.idi4.get_debounce_period, None, self.debounce_time.setValue, self.increase_error_count)
        async_call(self.idi4.get_value, None, self.show_new_value, self.increase_error_count)
        self.reconfigure_everything()
        async_call(self.idi4.set_interrupt, 0xFFFF, None, self.increase_error_count)

    def stop(self):
        async_call(self.idi4.set_interrupt, 0, None, self.increase_error_count)

    def get_url_part(self):
        return 'industrial_digital_in_4'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalIn4.DEVICE_IDENTIFIER
    
    def show_new_value(self, value):
        for i in range(16):
            if value & (1 << i):
                self.pin_buttons[i].setText('high')
                self.pin_button_icons[i].setPixmap(self.vcc_pixmap)
            else:
                self.pin_buttons[i].setText('low')
                self.pin_button_icons[i].setPixmap(self.gnd_pixmap)
    
    def reconfigure_everything_async(self, group):
        for i in range(4):
            if group[i] == 'n':
                self.groups[i].setCurrentIndex(0)
            else:
                item = 'Port ' + group[i].upper()
                index = self.groups[i].findText(item, Qt.MatchStartsWith)
                if index == -1:
                    self.groups[i].setCurrentIndex(0)
                else:
                    self.groups[i].setCurrentIndex(index)
                    
        if group[0] == 'n' and group[1] == 'n' and group[2] == 'n' and group[3]:
            self.show_buttons(0)
            self.hide_buttons(1)
            self.hide_buttons(2)
            self.hide_buttons(3)
        else:
            for i in range(4):
                if group[i] == 'n':
                    self.hide_buttons(i)
                else:
                    self.show_buttons(i)
    
    def reconfigure_everything(self):
        for i in range(4):
            self.groups[i].clear()
            self.groups[i].addItem('Off')
            for j in range(4):
                if self.available_ports & (1 << j):
                    item = 'Port ' + chr(ord('A') + j)
                    self.groups[i].addItem(item)
                    
        async_call(self.idi4.get_group, None, self.reconfigure_everything_async, self.increase_error_count)
            
    def show_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(True)
            self.pin_button_icons[i].setVisible(True)
            self.pin_button_labels[i].setVisible(True)
    
    def hide_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(False)
            self.pin_button_icons[i].setVisible(False)
            self.pin_button_labels[i].setVisible(False)
    
    def get_current_value(self):
        value = 0
        i = 0
        for b in self.pin_buttons:
            if 'low' in b.text():
                value |= (1 << i) 
            i += 1
        return value
    
    def set_group_pressed(self):
        group = ['n', 'n', 'n', 'n']
        for i in range(len(self.groups)):
            text = self.groups[i].currentText()
            if 'Port A' in text:
                group[i] = 'a' 
            elif 'Port B' in text:
                group[i] = 'b' 
            elif 'Port C' in text:
                group[i] = 'c' 
            elif 'Port D' in text:
                group[i] = 'd'
                 
        self.idi4.set_group(group)
        self.reconfigure_everything()
    
    def cb_interrupt(self, interrupt_mask, value_mask):
        self.show_new_value(value_mask)
        
    def debounce_go_pressed(self):
        time = self.debounce_time.value()
        self.idi4.set_debounce_period(time)
