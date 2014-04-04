# -*- coding: utf-8 -*-  
"""
IO-16 Plugin
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>

io16.py: IO-16 Plugin Implementation

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
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_io16 import BrickletIO16
from brickv.async_call import async_call

from PyQt4.QtCore import pyqtSignal, QTimer

from brickv.plugin_system.plugins.io16.ui_io16 import Ui_IO16
        
class IO16(PluginBase, Ui_IO16):
    qtcb_interrupt = pyqtSignal('char', int, int)
    qtcb_monoflop = pyqtSignal('char', int, int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'IO-16 Bricklet', version)
        
        self.setupUi(self)
        
        self.io = BrickletIO16(uid, ipcon)
        
        self.has_monoflop = version >= (1, 1, 2)
        
        self.qtcb_interrupt.connect(self.cb_interrupt)
        self.io.register_callback(self.io.CALLBACK_INTERRUPT,
                                  self.qtcb_interrupt.emit)
        
        self.port_value = { 'a': [self.av0, self.av1, self.av2, self.av3,
                                  self.av4, self.av5, self.av6, self.av7],
                            'b': [self.bv0, self.bv1, self.bv2, self.bv3,
                                  self.bv4, self.bv5, self.bv6, self.bv7]}
        
        self.port_direction = { 'a': [self.ad0, self.ad1, self.ad2, self.ad3,
                                      self.ad4, self.ad5, self.ad6, self.ad7],
                                'b': [self.bd0, self.bd1, self.bd2, self.bd3,
                                      self.bd4, self.bd5, self.bd6, self.bd7]}
        
        self.port_config = { 'a': [self.ac0, self.ac1, self.ac2, self.ac3,
                                   self.ac4, self.ac5, self.ac6, self.ac7],
                             'b': [self.bc0, self.bc1, self.bc2, self.bc3,
                                   self.bc4, self.bc5, self.bc6, self.bc7]}

        self.port_time = { 'a': [self.at0, self.at1, self.at2, self.at3,
                                 self.at4, self.at5, self.at6, self.at7],
                           'b': [self.bt0, self.bt1, self.bt2, self.bt3,
                                 self.bt4, self.bt5, self.bt6, self.bt7]}

        self.monoflop_active = { 'a': [False, False, False, False,
                                       False, False, False, False],
                                 'b': [False, False, False, False,
                                       False, False, False, False] }

        self.monoflop_timebefore = { 'a': [500, 500, 500, 500,
                                           500, 500, 500, 500],
                                     'b': [500, 500, 500, 500,
                                           500, 500, 500, 500] }

        self.init_async_generator = self.init_async()
        self.init_async_generator.next()
        
        self.save_button.pressed.connect(self.save_pressed)
        self.port_box.currentIndexChanged.connect(self.port_changed)
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
            self.go_button.setText("Go (FW Versiom >= 1.1.2 required)")
            self.go_button.setEnabled(False)
        else:
            self.update_timer.start()

        self.port_changed(0)
        
    def init_async(self):
        self.init_value = 0
        self.init_dir = 0
        self.init_config = 0
        self.init_monoflop = 0
        
        def get_port_async(value):
            self.init_value = value
            self.init_async_generator.next()
        
        def get_port_configuration_async(conf):
            self.init_dir, self.init_config = conf
            self.init_async_generator.next()
            
        def get_monoflop_async(init_monoflop):
            self.init_monoflop = init_monoflop
            self.init_async_generator.next()
        
        def get_debounce_period_async(debounce_period):
            self.debounce_edit.setText(str(debounce_period))
            self.port_changed(0)
        
        for port in ['a', 'b']:
            async_call(self.io.get_port, port, get_port_async, self.increase_error_count)
            yield
            async_call(self.io.get_port_configuration, port, get_port_configuration_async, self.increase_error_count)
            yield

            time = [0, 0, 0, 0, 0, 0, 0, 0]
            time_remaining = [0, 0, 0, 0, 0, 0, 0, 0]

            if self.has_monoflop:
                for pin in range(8):
                    async_call(self.io.get_port_monoflop, (port, pin), get_monoflop_async, self.increase_error_count)
                    yield

                    time[pin] = self.init_monoflop.time
                    time_remaining[pin] = self.init_monoflop.time_remaining

            self.init_values(port, self.init_value, self.init_dir, self.init_config, time, time_remaining)

        async_call(self.io.get_debounce_period, None, get_debounce_period_async, self.increase_error_count)
        
    def start(self):
        async_call(self.io.set_port_interrupt, ('a', 0xFF), None, self.increase_error_count)
        async_call(self.io.set_port_interrupt, ('b', 0xFF), None, self.increase_error_count)
        
        if self.has_monoflop:
            self.update_timer.start()

    def stop(self):
        async_call(self.io.set_port_interrupt, ('a', 0), None, self.increase_error_count)
        async_call(self.io.set_port_interrupt, ('b', 0), None, self.increase_error_count)

        self.update_timer.stop()

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'io16'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIO16.DEVICE_IDENTIFIER
    
    def init_values(self, port, value, dir, config, time, time_remaining):
        for i in range(8):
            if dir & (1 << i):
                self.port_direction[port][i].setText('Input')
                
                if config & (1 << i):
                    self.port_config[port][i].setText('Pull-Up')
                else:
                    self.port_config[port][i].setText('Default')
            else:
                self.port_direction[port][i].setText('Output')
                
                if config & (1 << i):
                    self.port_config[port][i].setText('High')
                else:
                    self.port_config[port][i].setText('Low')

            if value & (1 << i):
                self.port_value[port][i].setText('High')
            else:
                self.port_value[port][i].setText('Low')

            self.port_time[port][i].setText(str(time_remaining[i]))

            if time[i] > 0:
                self.monoflop_timebefore[port][i] = time[i]

            if time_remaining[i] > 0:
                self.monoflop_active[port][i] = True

        self.update_monoflop_ui_state()

    def update_monoflop_ui_state(self):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())

        if self.port_direction[port][pin].text() == 'Output' and \
           self.direction_box.currentText() == 'Output' and \
           self.has_monoflop:
            self.time_spinbox.setEnabled(not self.monoflop_active[port][pin])
            self.go_button.setEnabled(True)
        else:
            self.time_spinbox.setEnabled(False)
            self.go_button.setEnabled(False)

        self.time_spinbox.setValue(self.monoflop_timebefore[port][pin])

    def save_pressed(self):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())
        direction = str(self.direction_box.currentText())[0].lower()
        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[port][pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull-Up'
            
        try:
            self.io.set_port_configuration(port, 1 << pin, direction, value)
        except ip_connection.Error:
            return
            
        self.port_direction[port][pin].setText(self.direction_box.currentText())
        self.port_config[port][pin].setText(self.value_box.currentText())

        self.monoflop_active[port][pin] = False
        self.port_time[port][pin].setText('0')

        self.update_monoflop_ui_state()

    def cb_interrupt(self, port, interrupt, value):
        for i in range(8):
            if interrupt & (1 << i):
                if value & (1 << i):
                    self.port_value[port][i].setText('High')
                else:
                    self.port_value[port][i].setText('Low')
    
    def port_changed(self, port):
        self.pin_changed(int(self.pin_box.currentText()))
                    
    def pin_changed(self, pin):
        port = str(self.port_box.currentText()).lower()
        
        if str(self.port_direction[port][pin].text()) == 'Input':
            index = 0
        else:
            index = 1
            
        self.direction_box.setCurrentIndex(index)
        self.direction_changed(index)
        self.update_monoflop_ui_state()
        
    def direction_changed(self, direction):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())
        
        self.value_box.clear()

        if direction == 1:
            self.value_box.addItem('High')
            self.value_box.addItem('Low')

            if str(self.port_config[port][pin].text()) == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_box.addItem('Pull-Up')
            self.value_box.addItem('Default')

            if str(self.port_config[port][pin].text()) == 'Pull-Up':
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
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())

        if not self.monoflop_active[port][pin]:
            self.monoflop_timebefore[port][pin] = time

    def go_pressed(self):
        port = str(self.port_box.currentText()).lower()
        pin = int(self.pin_box.currentText())

        if self.value_box.currentText() == 'High':
            value = 1
        else:
            value = 0

        try:
            time = self.monoflop_timebefore[port][pin]
            self.io.set_port_monoflop(port, 1 << pin, value << pin, time)

            if value:
                self.port_value[port][pin].setText('High')
                self.port_config[port][pin].setText('High')
            else:
                self.port_value[port][pin].setText('Low')
                self.port_config[port][pin].setText('Low')

            self.monoflop_active[port][pin] = True
            self.time_spinbox.setEnabled(False)
            self.port_time[port][pin].setText(str(time))
        except ip_connection.Error:
            return

    def cb_monoflop(self, port, pin_mask, value_mask):
        for pin in range(8):
            if pin_mask & (1 << pin):
                self.monoflop_active[port][pin] = False
                self.port_time[port][pin].setText('0')

                if port == str(self.port_box.currentText()).lower() and \
                   pin == int(self.pin_box.currentText()):
                    self.time_spinbox.setValue(self.monoflop_timebefore[port][pin])
                    self.time_spinbox.setEnabled(True)

                if value_mask & (1 << pin):
                    self.port_value[port][pin].setText('High')
                    self.port_config[port][pin].setText('High')
                else:
                    self.port_value[port][pin].setText('Low')
                    self.port_config[port][pin].setText('Low')

    def update_async(self, port, pin, monoflop):
        selected_port = str(self.port_box.currentText()).lower()
        selected_pin = int(self.pin_box.currentText())
        
        _, _, time_remaining = monoflop
        if port == selected_port and pin == selected_pin and self.monoflop_active[port][pin]:
            self.time_spinbox.setValue(time_remaining)

        self.port_time[port][pin].setText(str(time_remaining))

    def update(self):
        for port in ['a', 'b']:
            for pin in range(8):
                if self.monoflop_active[port][pin]:
                    def get_lambda(port, pin):
                        return lambda x: self.update_async(port, pin, x)
                    
                    async_call(self.io.get_port_monoflop, (port, pin), get_lambda(port, pin), self.increase_error_count)
