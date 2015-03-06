# -*- coding: utf-8 -*-  
"""
Industrial Digital Out 4 Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

industrial_digital_out_4.py: Industrial Digital Out 4 Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_industrial_digital_out_4 import BrickletIndustrialDigitalOut4
from brickv.async_call import async_call

from PyQt4.QtCore import Qt, pyqtSignal, QTimer

from brickv.plugin_system.plugins.industrial_digital_out_4.ui_industrial_digital_out_4 import Ui_IndustrialDigitalOut4
from brickv.bmp_to_pixmap import bmp_to_pixmap

class IndustrialDigitalOut4(PluginBase, Ui_IndustrialDigitalOut4):
    qtcb_monoflop = pyqtSignal(int, int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIndustrialDigitalOut4, *args)

        self.setupUi(self)
        
        self.ido4 = self.device
        
        self.gnd_pixmap = bmp_to_pixmap('plugin_system/plugins/industrial_digital_out_4/dio_gnd.bmp')
        self.vcc_pixmap = bmp_to_pixmap('plugin_system/plugins/industrial_digital_out_4/dio_vcc.bmp')
        
        self.pin_buttons = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b10, self.b11, self.b12, self.b13, self.b14, self.b15]
        self.pin_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon, self.b4_icon, self.b5_icon, self.b6_icon, self.b7_icon, self.b8_icon, self.b9_icon, self.b10_icon, self.b11_icon, self.b12_icon, self.b13_icon, self.b14_icon, self.b15_icon]
        self.pin_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label, self.b4_label, self.b5_label, self.b6_label, self.b7_label, self.b8_label, self.b9_label, self.b10_label, self.b11_label, self.b12_label, self.b13_label, self.b14_label, self.b15_label]
        self.groups = [self.group0, self.group1, self.group2, self.group3]
        for icon in self.pin_button_icons:
            icon.setPixmap(self.gnd_pixmap)
            icon.show()

        self.lines = [[self.line0, self.line0a, self.line0b, self.line0c],
                      [self.line1, self.line1a, self.line1b, self.line1c],
                      [self.line2, self.line2a, self.line2b, self.line2c],
                      [self.line3, self.line3a, self.line3b, self.line3c]]
        for lines in self.lines:
            for line in lines:
                line.setVisible(False)

        self.available_ports = 0
        async_call(self.ido4.get_available_for_group, None, self.get_available_for_group_aysnc, self.increase_error_count)
        
        def get_button_lambda(button):
            return lambda: self.pin_button_clicked(button)
        
        for i in range(len(self.pin_buttons)):
            self.pin_buttons[i].clicked.connect(get_button_lambda(i))
        
        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.ido4.register_callback(self.ido4.CALLBACK_MONOFLOP_DONE,
                                    self.qtcb_monoflop.emit)
        
        self.set_group.clicked.connect(self.set_group_clicked)
        
        self.monoflop_pin.currentIndexChanged.connect(self.monoflop_pin_changed)
        self.monoflop_go.clicked.connect(self.monoflop_go_clicked)
        self.monoflop_time_before = [1000] * 16
        self.monoflop_pending = [False] * 16
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        self.reconfigure_everything()

    def get_available_for_group_aysnc(self, available_ports):
        self.available_ports = available_ports

    def start(self):
        self.reconfigure_everything()

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    def get_url_part(self):
        return 'industrial_digital_out_4'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalOut4.DEVICE_IDENTIFIER

    def reconfigure_everything_async3(self, pin, value, time, time_remaining):
        index = self.monoflop_pin.findText('Pin {0}'.format(pin))
        if index >= 0:
            if time_remaining > 0:
                self.monoflop_pending[pin] = True
                self.monoflop_time_before[pin] = time

                self.monoflop_pin.setCurrentIndex(index)
                self.monoflop_time.setValue(time_remaining)
                self.monoflop_time.setEnabled(False)

                self.update_timer.start()
            else:
                self.monoflop_pending[pin] = False

    def reconfigure_everything_async2(self, value_mask):
        for pin in range(16):
            if value_mask & (1 << pin):
                self.pin_buttons[pin].setText('Switch Low')
                self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
            else:
                self.pin_buttons[pin].setText('Switch High')
                self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

            index = self.monoflop_pin.findText('Pin {0}'.format(pin))
            if index >= 0:
                def get_monoflop_lambda(pin):
                    return lambda monoflop: self.reconfigure_everything_async3(pin, *monoflop)
                async_call(self.ido4.get_monoflop, pin, get_monoflop_lambda(pin), self.increase_error_count)

    def reconfigure_everything_async1(self, group):
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

        self.monoflop_pin.setCurrentIndex(0)

        async_call(self.ido4.get_value, None, self.reconfigure_everything_async2, self.increase_error_count)

    def reconfigure_everything(self):
        for i in range(4):
            self.groups[i].clear()
            self.groups[i].addItem('Off')
            for j in range(4):
                if self.available_ports & (1 << j):
                    item = 'Port ' + chr(ord('A') + j)
                    self.groups[i].addItem(item)
                    
        async_call(self.ido4.get_group, None, self.reconfigure_everything_async1, self.increase_error_count)

    def show_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(True)
            self.pin_button_icons[i].setVisible(True)
            self.pin_button_labels[i].setVisible(True)

        for line in self.lines[num]:
            line.setVisible(True)
    
    def hide_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(False)
            self.pin_button_icons[i].setVisible(False)
            self.pin_button_labels[i].setVisible(False)

        for line in self.lines[num]:
            line.setVisible(False)
    
    def get_current_value(self):
        value = 0
        i = 0
        for b in self.pin_buttons:
            if 'Low' in b.text():
                value |= (1 << i) 
            i += 1
        return value
    
    def set_group_clicked(self):
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
                 
        self.ido4.set_group(group)
        self.reconfigure_everything()
    
    def pin_button_clicked(self, button):
        value = self.get_current_value()
        if 'High' in self.pin_buttons[button].text():
            value |= (1 << button)
            self.pin_buttons[button].setText('Switch Low')
            self.pin_button_icons[button].setPixmap(self.vcc_pixmap)
        else:
            value &= ~(1 << button)
            self.pin_buttons[button].setText('Switch High')
            self.pin_button_icons[button].setPixmap(self.gnd_pixmap)
            
        self.ido4.set_value(value)
        self.update_timer.stop()

        for pin in range(16):
            self.monoflop_pending[pin] = False

        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        self.monoflop_time.setValue(self.monoflop_time_before[pin])
        self.monoflop_time.setEnabled(True)

    def cb_monoflop(self, pin_mask, value_mask):
        for pin in range(16):
            if (1 << pin) & pin_mask:
                self.monoflop_pending[pin] = False

                if (1 << pin) & value_mask:
                    self.pin_buttons[pin].setText('Switch Low')
                    self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
                else:
                    self.pin_buttons[pin].setText('Switch High')
                    self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

        if sum(self.monoflop_pending) == 0:
            self.update_timer.stop()

        current_pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if (1 << current_pin) & pin_mask:
            self.monoflop_time.setValue(self.monoflop_time_before[current_pin])
            self.monoflop_time.setEnabled(True)

    def monoflop_pin_changed_async(self, monoflop):
        _, _, time_remaining = monoflop
        self.monoflop_time.setValue(time_remaining)

    def monoflop_pin_changed(self):
        try:
            pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        except ValueError:
            return

        if self.monoflop_pending[pin]:
            async_call(self.ido4.get_monoflop, pin, self.monoflop_pin_changed_async, self.increase_error_count)
            self.monoflop_time.setEnabled(False)
        else:
            self.monoflop_time.setValue(self.monoflop_time_before[pin])
            self.monoflop_time.setEnabled(True)

    def monoflop_go_clicked(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        if self.monoflop_pending[pin]:
            time = self.monoflop_time_before[pin]
        else:
            time = self.monoflop_time.value()

        value = self.monoflop_state.currentIndex() == 0

        self.monoflop_time.setEnabled(False)
        self.monoflop_time_before[pin] = time
        self.monoflop_pending[pin] = True
        self.ido4.set_monoflop(1 << pin, value << pin, time)

        if value:
            self.pin_buttons[pin].setText('Switch Low')
            self.pin_button_icons[pin].setPixmap(self.vcc_pixmap)
        else:
            self.pin_buttons[pin].setText('Switch High')
            self.pin_button_icons[pin].setPixmap(self.gnd_pixmap)

        self.update_timer.start()

    def update_async(self, pin, value, time, time_remaining):
        if self.monoflop_pending[pin]:
            self.monoflop_time.setValue(time_remaining)

    def update(self):
        pin = int(self.monoflop_pin.currentText().replace('Pin ', ''))
        async_call(self.ido4.get_monoflop, pin, lambda monoflop: self.update_async(pin, *monoflop), self.increase_error_count)
