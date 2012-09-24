# -*- coding: utf-8 -*-  
"""
IO4 Plugin
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

humidity.py: IO4 Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import pyqtSignal, QTimer
from ui_io4 import Ui_IO4

from bindings import bricklet_io4
        
class IO4(PluginBase, Ui_IO4):
    qtcb_interrupt = pyqtSignal(int, int)
    qtcb_monoflop = pyqtSignal(int, int)
    
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.setupUi(self)
        
        self.io = bricklet_io4.IO4(self.uid)
        self.ipcon.add_device(self.io)
        version = self.io.get_version()[1]
        self.version = '.'.join(map(str, version))
        self.has_monoflop = version[1] > 1 or (version[1] == 1 and version[2] > 0)
        
        self.qtcb_interrupt.connect(self.cb_interrupt)
        self.io.register_callback(self.io.CALLBACK_INTERRUPT,
                                  self.qtcb_interrupt.emit)
        
        self.port_value = [self.av0, self.av1, self.av2, self.av3]
        self.port_direction = [self.ad0, self.ad1, self.ad2, self.ad3]
        self.port_config = [self.ac0, self.ac1, self.ac2, self.ac3]
        self.port_time = [self.at0, self.at1, self.at2, self.at3]

        self.monoflop_active = [False, False, False, False]
        self.monoflop_timebefore = [500, 500, 500, 500]

        try:
            value = self.io.get_value()
            dir, config = self.io.get_configuration()
            time = [0, 0, 0, 0]
            time_remaining = [0, 0, 0, 0]

            if self.has_monoflop:
                for pin in range(4):
                    monoflop = self.io.get_monoflop(pin)
                    time[pin] = monoflop.time
                    time_remaining[pin] = monoflop.time_remaining

            self.init_values(value, dir, config, time, time_remaining)

            debounce = self.io.get_debounce_period()
            self.debounce_edit.setText(str(debounce))
        except ip_connection.Error:
            pass
        
        self.save_button.pressed.connect(self.save_pressed)
        self.pin_box.currentIndexChanged.connect(self.pin_changed)
        self.direction_box.currentIndexChanged.connect(self.direction_changed)
        self.debounce_save.pressed.connect(self.debounce_save_pressed)
        self.time_spinbox.valueChanged.connect(self.time_changed)
        self.go_button.pressed.connect(self.go_pressed)

        self.qtcb_monoflop.connect(self.cb_monoflop)
        self.io.register_callback(self.io.CALLBACK_MONOFLOP_DONE,
                                  self.qtcb_monoflop.emit)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update)
        self.update_timer.setInterval(50)

        if not self.has_monoflop:
            self.go_button.setText("Go (> 1.1.0 needed)")
            self.go_button.setEnabled(False)
        else:
            self.update_timer.start()
        
        self.pin_changed(0)
        
    def start(self):
        try:
            self.io.set_interrupt(1 | 2 | 4 | 8)
        except ip_connection.Error:
            return

        if self.has_monoflop:
            self.update_timer.start()
        
    def stop(self):
        try:
            self.io.set_interrupt(0)
        except ip_connection.Error:
            return

        self.update_timer.stop()

    @staticmethod
    def has_name(name):
        return 'IO-4 Bricklet' in name 
    
    def init_values(self, value, dir, config, time, time_remaining):
        for i in range(4):
            if dir & (1 << i):
                self.port_direction[i].setText('Input')
                
                if config & (1 << i):
                    self.port_config[i].setText('Pull-Up')
                else:
                    self.port_config[i].setText('Default')
            else:
                self.port_direction[i].setText('Output')
                
                if config & (1 << i):
                    self.port_config[i].setText('High')
                else:
                    self.port_config[i].setText('Low')

            if value & (1 << i):
                self.port_value[i].setText('High')
            else:
                self.port_value[i].setText('Low')

            self.port_time[i].setText(str(time_remaining[i]))

            if time[i] > 0:
                self.monoflop_timebefore[i] = time[i]

            if time_remaining[i] > 0:
                self.monoflop_active[i] = True

        self.update_monoflop_ui_state()

    def update_monoflop_ui_state(self):
        pin = int(self.pin_box.currentText())

        if self.port_direction[pin].text() == 'Output' and \
           self.direction_box.currentText() == 'Output' and \
           self.has_monoflop:
            self.time_spinbox.setEnabled(not self.monoflop_active[pin])
            self.go_button.setEnabled(True)
        else:
            self.time_spinbox.setEnabled(False)
            self.go_button.setEnabled(False)

        self.time_spinbox.setValue(self.monoflop_timebefore[pin])

    def save_pressed(self):
        pin = int(self.pin_box.currentText())
        direction = str(self.direction_box.currentText())[0].lower()
        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull-Up'
            
        try:
            self.io.set_configuration(1 << pin, direction, value)
        except ip_connection.Error:
            return
            
        self.port_direction[pin].setText(self.direction_box.currentText())
        self.port_config[pin].setText(self.value_box.currentText())

        self.monoflop_active[pin] = False
        self.port_time[pin].setText('0')

        self.update_monoflop_ui_state()
        
    def cb_interrupt(self, interrupt, value):
        for i in range(4):
            if interrupt & (1 << i):
                if value & (1 << i):
                    self.port_value[i].setText('High')
                else:
                    self.port_value[i].setText('Low')
    
    def pin_changed(self, pin):
        if str(self.port_direction[pin].text()) == 'Input':
            index = 0
        else:
            index = 1
            
        self.direction_box.setCurrentIndex(index)
        self.direction_changed(index)
        self.update_monoflop_ui_state()
        
    def direction_changed(self, direction):
        pin = int(self.pin_box.currentText())

        self.value_box.clear()

        if direction == 1:
            self.value_box.addItem('High')
            self.value_box.addItem('Low')

            if str(self.port_config[pin].text()) == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_box.addItem('Pull-Up')
            self.value_box.addItem('Default')

            if str(self.port_config[pin].text()) == 'Pull-Up':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)

        self.update_monoflop_ui_state()

    def debounce_save_pressed(self):
        debounce = int(str(self.debounce_edit.text()))
        try:
            self.io.set_debounce_period(debounce)
        except ip_connection.Error:
            return

    def time_changed(self, time):
        pin = int(self.pin_box.currentText())

        if not self.monoflop_active[pin]:
            self.monoflop_timebefore[pin] = time

    def go_pressed(self):
        pin = int(self.pin_box.currentText())

        if self.value_box.currentText() == 'High':
            value = 1
        else:
            value = 0

        try:
            time = self.monoflop_timebefore[pin]
            self.io.set_monoflop(1 << pin, value << pin, time)

            if value:
                self.port_value[pin].setText('High')
                self.port_config[pin].setText('High')
            else:
                self.port_value[pin].setText('Low')
                self.port_config[pin].setText('Low')

            self.monoflop_active[pin] = True
            self.time_spinbox.setEnabled(False)
            self.port_time[pin].setText(str(time))
        except ip_connection.Error:
            return

    def cb_monoflop(self, pin_mask, value_mask):
        for pin in range(4):
            if pin_mask & (1 << pin):
                self.monoflop_active[pin] = False
                self.port_time[pin].setText('0')

                if pin == int(self.pin_box.currentText()):
                    self.time_spinbox.setValue(self.monoflop_timebefore[pin])
                    self.time_spinbox.setEnabled(True)

                if value_mask & (1 << pin):
                    self.port_value[pin].setText('High')
                    self.port_config[pin].setText('High')
                else:
                    self.port_value[pin].setText('Low')
                    self.port_config[pin].setText('Low')

    def update(self):
        selected_pin = int(self.pin_box.currentText())

        for pin in range(4):
            if self.monoflop_active[pin]:
                try:
                    value, time, time_remaining = self.io.get_monoflop(pin)
                except ip_connection.Error:
                    continue

                if pin == selected_pin:
                    self.time_spinbox.setValue(time_remaining)

                self.port_time[pin].setText(str(time_remaining))
