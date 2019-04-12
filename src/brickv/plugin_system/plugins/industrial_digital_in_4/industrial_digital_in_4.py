# -*- coding: utf-8 -*-
"""
Industrial Digital In 4 Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt5.QtCore import Qt

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.industrial_digital_in_4.ui_industrial_digital_in_4 import Ui_IndustrialDigitalIn4
from brickv.bindings.bricklet_industrial_digital_in_4 import BrickletIndustrialDigitalIn4
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.load_pixmap import load_masked_pixmap

class IndustrialDigitalIn4(PluginBase, Ui_IndustrialDigitalIn4):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIndustrialDigitalIn4, *args)

        self.setupUi(self)

        self.idi4 = self.device

        self.gnd_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_digital_in_4/dio_gnd.bmp')
        self.vcc_pixmap = load_masked_pixmap('plugin_system/plugins/industrial_digital_in_4/dio_vcc.bmp')

        self.pin_buttons = [self.b0, self.b1, self.b2, self.b3, self.b4, self.b5, self.b6, self.b7, self.b8, self.b9, self.b10, self.b11, self.b12, self.b13, self.b14, self.b15]
        self.pin_button_icons = [self.b0_icon, self.b1_icon, self.b2_icon, self.b3_icon, self.b4_icon, self.b5_icon, self.b6_icon, self.b7_icon, self.b8_icon, self.b9_icon, self.b10_icon, self.b11_icon, self.b12_icon, self.b13_icon, self.b14_icon, self.b15_icon]
        self.pin_button_labels = [self.b0_label, self.b1_label, self.b2_label, self.b3_label, self.b4_label, self.b5_label, self.b6_label, self.b7_label, self.b8_label, self.b9_label, self.b10_label, self.b11_label, self.b12_label, self.b13_label, self.b14_label, self.b15_label]
        self.groups = [self.group0, self.group1, self.group2, self.group3]

        self.lines = [[self.line0, self.line0a, self.line0b, self.line0c],
                      [self.line1, self.line1a, self.line1b, self.line1c],
                      [self.line2, self.line2a, self.line2b, self.line2c],
                      [self.line3, self.line3a, self.line3b, self.line3c]]
        for lines in self.lines:
            for line in lines:
                line.setVisible(False)

        self.available_ports = 0
        async_call(self.idi4.get_available_for_group, None, self.get_available_for_group_aysnc, self.increase_error_count)

        self.cbe_value = CallbackEmulator(self.idi4.get_value,
                                          None,
                                          self.cb_value,
                                          self.increase_error_count)

        self.set_group.clicked.connect(self.set_group_clicked)

        self.debounce_go.clicked.connect(self.debounce_go_clicked)

        self.reconfigure_everything()

    def get_available_for_group_aysnc(self, available_ports):
        self.available_ports = available_ports

    def start(self):
        async_call(self.idi4.get_debounce_period, None, self.debounce_time.setValue, self.increase_error_count)

        self.reconfigure_everything()

        self.cbe_value.set_period(50)

    def stop(self):
        self.cbe_value.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIndustrialDigitalIn4.DEVICE_IDENTIFIER

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

        if group[0] == 'n' and group[1] == 'n' and group[2] == 'n' and group[3] == 'n':
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

        for line in self.lines[num]:
            line.setVisible(True)

    def hide_buttons(self, num):
        for i in range(num*4, (num+1)*4):
            self.pin_buttons[i].setVisible(False)
            self.pin_button_icons[i].setVisible(False)
            self.pin_button_labels[i].setVisible(False)

        for line in self.lines[num]:
            line.setVisible(False)

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

        self.idi4.set_group(group)
        self.reconfigure_everything()

    def cb_value(self, value_mask):
        for i in range(16):
            if value_mask & (1 << i):
                self.pin_buttons[i].setText('High')
                self.pin_button_icons[i].setPixmap(self.vcc_pixmap)
            else:
                self.pin_buttons[i].setText('Low')
                self.pin_button_icons[i].setPixmap(self.gnd_pixmap)

    def debounce_go_clicked(self):
        time = self.debounce_time.value()
        self.idi4.set_debounce_period(time)
