# -*- coding: utf-8 -*-  
"""
Industrial Quad Relay Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

industrial_quad_relay.py: Industrial Quad Relay Plugin Implementation

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
from bindings.bricklet_industrial_quad_relay import BrickletIndustrialQuadRelay
from async_call import async_call

from PyQt4.QtCore import Qt, pyqtSignal, QTimer

from ui_industrial_quad_relay import Ui_IndustrialQuadRelay
from relay_open_pixmap import get_relay_open_pixmap
from relay_close_pixmap import get_relay_close_pixmap

class IndustrialQuadRelay(PluginBase, Ui_IndustrialQuadRelay):
    qtcb_monoflop = pyqtSignal(int, bool)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Industrial Quad Relay Bricklet', version)
        
        self.setupUi(self)
        
        self.iqr = BrickletIndustrialQuadRelay(uid, ipcon)
        
        self.open_pixmap = get_relay_open_pixmap()
        self.close_pixmap = get_relay_close_pixmap()
        
        self.relay_buttons = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b10, self.b11, self.b12, self.b13, self.b14, self.b15]
        self.relay_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon, self.b4_icon, self.b5_icon, self.b6_icon, self.b7_icon, self.b8_icon, self.b9_icon, self.b10_icon, self.b11_icon, self.b12_icon, self.b13_icon, self.b14_icon, self.b15_icon]
        self.relay_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label, self.b4_label, self.b5_label, self.b6_label, self.b7_label, self.b8_label, self.b9_label, self.b10_label, self.b11_label, self.b12_label, self.b13_label, self.b14_label, self.b15_label]
        self.groups = [self.group0, self.group1, self.group2, self.group3]
        for icon in self.relay_button_icons:
            icon.setPixmap(self.open_pixmap)
            icon.show()

        self.lines = [[self.line0, self.line0a, self.line0b, self.line0c],
                      [self.line1, self.line1a, self.line1b, self.line1c],
                      [self.line2, self.line2a, self.line2b, self.line2c],
                      [self.line3, self.line3a, self.line3b, self.line3c]]
        for lines in self.lines:
            for line in lines:
                line.setVisible(False)
        
        self.available_ports = 0
        async_call(self.iqr.get_available_for_group, None, self.get_available_for_group_aysnc, self.increase_error_count)
        
        def get_button_lambda(button):
            return lambda: self.relay_button_pressed(button)
        
        for i in range(len(self.relay_buttons)):
            self.relay_buttons[i].pressed.connect(get_button_lambda(i))
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.iqr.register_callback(self.iqr.CALLBACK_MONOFLOP_DONE,
                                   self.qtcb_monoflop.emit)
        
        self.set_group.pressed.connect(self.set_group_pressed)
        
        self.monoflop_go.pressed.connect(self.monoflop_go_pressed)
        self.monoflop_time_before = 1000
        
        self.reconfigure_everything()
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

    def get_available_for_group_aysnc(self, available_ports):
        self.available_ports = available_ports

    def start(self):
        self.reconfigure_everything()

    def stop(self):
        pass

    def get_url_part(self):
        return 'industrial_quad_relay'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialQuadRelay.DEVICE_IDENTIFIER
    
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

        self.monoflop_pin.clear()

        if group[0] == 'n' and group[1] == 'n' and group[2] == 'n' and group[3] == 'n':
            self.show_buttons(0)
            self.hide_buttons(1)
            self.hide_buttons(2)
            self.hide_buttons(3)
            self.monoflop_pin.addItem('Pin 0')
            self.monoflop_pin.addItem('Pin 1')
            self.monoflop_pin.addItem('Pin 2')
            self.monoflop_pin.addItem('Pin 3')
        else:
            for i in range(4):
                if group[i] == 'n':
                    self.hide_buttons(i)
                else:
                    for j in range(4):
                        self.monoflop_pin.addItem('Pin ' + str(i*4+j))
                    self.show_buttons(i)
                    
    def reconfigure_everything(self):
        for i in range(4):
            self.groups[i].clear()
            self.groups[i].addItem('Off')
            for j in range(4):
                if self.available_ports & (1 << j):
                    item = 'Port ' + chr(ord('A') + j)
                    self.groups[i].addItem(item)
                    
        async_call(self.iqr.get_group, None, self.reconfigure_everything_async, self.increase_error_count)
            
    def show_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.relay_buttons[i].setVisible(True)
            self.relay_button_icons[i].setVisible(True)
            self.relay_button_labels[i].setVisible(True)

        for line in self.lines[num]:
            line.setVisible(True)

    def hide_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.relay_buttons[i].setVisible(False)
            self.relay_button_icons[i].setVisible(False)
            self.relay_button_labels[i].setVisible(False)

        for line in self.lines[num]:
            line.setVisible(False)

    def get_current_value(self):
        value = 0
        i = 0
        for b in self.relay_buttons:
            if 'Off' in b.text():
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
                 
        self.iqr.set_group(group)
        self.reconfigure_everything()
    
    def relay_button_pressed(self, button):
        value = self.get_current_value()
        if 'On' in self.relay_buttons[button].text():
            value |= (1 << button)
            self.relay_buttons[button].setText('Off')
            self.relay_button_icons[button].setPixmap(self.close_pixmap)
        else:
            value &= ~(1 << button)
            self.relay_buttons[button].setText('On')
            self.relay_button_icons[button].setPixmap(self.open_pixmap)
            
        self.iqr.set_value(value)
        
    def cb_monoflop(self, pin_mask, value_mask):
        self.monoflop_time.setValue(self.monoflop_time_before)
        self.update_timer.stop()
        self.monoflop_time.setEnabled(True)
        self.monoflop_pin.setEnabled(True)
        
        for pin in range(16):
            if (1 << pin) & pin_mask:
                if 'On' in self.relay_buttons[pin].text():
                    self.relay_buttons[pin].setText('Off')
                    self.relay_button_icons[pin].setPixmap(self.close_pixmap)
                else:
                    self.relay_buttons[pin].setText('On')
                    self.relay_button_icons[pin].setPixmap(self.open_pixmap)
                    
                self.relay_buttons[pin].setEnabled(True)
        
    def monoflop_go_pressed(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if self.update_timer.isActive():
            time = self.monoflop_time_before
        else:
            time = self.monoflop_time.value()
        value = 'On' in (self.relay_buttons[pin].text())
        
        self.monoflop_time.setEnabled(False)
        self.monoflop_pin.setEnabled(False)
        self.monoflop_time_before = time
        self.iqr.set_monoflop(1 << pin, value << pin, time)
            
        if not self.update_timer.isActive():
            self.relay_buttons[pin].setEnabled(False)
            if 'On' in self.relay_buttons[pin].text():
                self.relay_buttons[pin].setText('Off')
                self.relay_button_icons[pin].setPixmap(self.close_pixmap)
            else:
                self.relay_buttons[pin].setText('On')
                self.relay_button_icons[pin].setPixmap(self.open_pixmap)
        self.update_timer.start()
    
    def update_async(self, monoflop):
        _, _, time_remaining = monoflop
        self.monoflop_time.setValue(time_remaining)
        
    def update(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        async_call(self.iqr.get_monoflop, pin, self.update_async, self.increase_error_count)
