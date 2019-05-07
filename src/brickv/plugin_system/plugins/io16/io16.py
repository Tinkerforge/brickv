# -*- coding: utf-8 -*-
"""
IO-16 Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012, 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

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

import functools

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QSpinBox, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.io16.ui_io16 import Ui_IO16
from brickv.bindings.bricklet_io16 import BrickletIO16
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.monoflop import Monoflop

class IO16Wrapper:
    CALLBACK_MONOFLOP_DONE = BrickletIO16.CALLBACK_MONOFLOP_DONE

    def __init__(self, device, port, qtcb_monoflop_done):
        self.device = device
        self.port = port
        self.monoflop_done_callback = None

        qtcb_monoflop_done.connect(self.cb_monoflop_done)

    def set_monoflop(self, selection_mask, value_mask, time):
        self.device.set_port_monoflop(self.port, selection_mask, value_mask, time)

    def get_monoflop(self, pin):
        return self.device.get_port_monoflop(self.port, pin)

    def register_callback(self, callback_id, function):
        if callback_id == self.CALLBACK_MONOFLOP_DONE:
            self.monoflop_done_callback = function

    def cb_monoflop_done(self, port, selection_mask, value_mask):
        if port.lower() == self.port and self.monoflop_done_callback != None:
            self.monoflop_done_callback(selection_mask, value_mask)

class IO16(PluginBase, Ui_IO16):
    qtcb_monoflop_done = pyqtSignal(str, int, int)

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIO16, *args)

        self.setupUi(self)

        self.io = self.device

        self.io.register_callback(self.io.CALLBACK_MONOFLOP_DONE,
                                  self.qtcb_monoflop_done.emit)

        self.io_wrapper = {
            'a': IO16Wrapper(self.io, 'a', self.qtcb_monoflop_done),
            'b': IO16Wrapper(self.io, 'b', self.qtcb_monoflop_done),
        }

        self.cbe_port_a = CallbackEmulator(self.io.get_port,
                                           'a',
                                           self.cb_port,
                                           self.increase_error_count,
                                           pass_arguments_to_result_callback=True)
        self.cbe_port_b = CallbackEmulator(self.io.get_port,
                                           'b',
                                           self.cb_port,
                                           self.increase_error_count,
                                           pass_arguments_to_result_callback=True)

        self.port_value = {
            'a': [self.av0, self.av1, self.av2, self.av3,
                  self.av4, self.av5, self.av6, self.av7],
            'b': [self.bv0, self.bv1, self.bv2, self.bv3,
                  self.bv4, self.bv5, self.bv6, self.bv7]
        }

        self.port_direction = {
            'a': [self.ad0, self.ad1, self.ad2, self.ad3,
                  self.ad4, self.ad5, self.ad6, self.ad7],
            'b': [self.bd0, self.bd1, self.bd2, self.bd3,
                  self.bd4, self.bd5, self.bd6, self.bd7]
        }

        self.port_config = {
            'a': [self.ac0, self.ac1, self.ac2, self.ac3,
                  self.ac4, self.ac5, self.ac6, self.ac7],
            'b': [self.bc0, self.bc1, self.bc2, self.bc3,
                  self.bc4, self.bc5, self.bc6, self.bc7]
        }

        self.port_time = {
            'a': [self.at0, self.at1, self.at2, self.at3,
                  self.at4, self.at5, self.at6, self.at7],
            'b': [self.bt0, self.bt1, self.bt2, self.bt3,
                  self.bt4, self.bt5, self.bt6, self.bt7]
        }

        self.save_button.clicked.connect(self.save_clicked)
        self.pin_box.currentIndexChanged.connect(self.pin_changed)
        self.direction_box.currentIndexChanged.connect(self.direction_changed)
        self.debounce_save.clicked.connect(self.debounce_save_clicked)
        self.go_button.clicked.connect(self.go_clicked)

        self.monoflop_values = {'a': [], 'b': []}
        self.monoflop_times = {'a': [], 'b': []}
        self.monoflop = {}

        for port in ['a', 'b']:
            for i in range(8):
                monoflop_value = QComboBox()
                monoflop_value.addItem('High', 1)
                monoflop_value.addItem('Low', 0)

                self.monoflop_values[port].append(monoflop_value)
                self.monoflop_value_stack.addWidget(monoflop_value)

                monoflop_time = QSpinBox()
                monoflop_time.setRange(1, (1 << 31) - 1)
                monoflop_time.setValue(1000)

                self.monoflop_times[port].append(monoflop_time)
                self.monoflop_time_stack.addWidget(monoflop_time)

            self.monoflop[port] = Monoflop(self.io_wrapper[port],
                                           [0, 1, 2, 3, 4, 5, 6, 7],
                                           self.monoflop_values[port],
                                           functools.partial(self.cb_value_change_by_monoflop, port),
                                           self.monoflop_times[port],
                                           self.port_time[port],
                                           self,
                                           setter_uses_bitmasks=True,
                                           callback_uses_bitmasks=True)

        self.pin_changed(0)

    def init_async(self):
        self.init_value = 0
        self.init_dir = 0
        self.init_config = 0

        def get_port_async(value):
            self.init_value = value
            next(self.init_async_generator)

        def get_port_configuration_async(conf):
            self.init_dir, self.init_config = conf
            next(self.init_async_generator)

        def get_debounce_period_async(debounce_period):
            self.debounce_edit.setText(str(debounce_period))
            self.pin_changed(0)

        for port in ['a', 'b']:
            async_call(self.io.get_port, port, get_port_async, self.increase_error_count)
            yield

            async_call(self.io.get_port_configuration, port, get_port_configuration_async, self.increase_error_count)
            yield

            self.init_values(port, self.init_value, self.init_dir, self.init_config)

        async_call(self.io.get_debounce_period, None, get_debounce_period_async, self.increase_error_count)

    def start(self):
        self.init_async_generator = self.init_async()
        next(self.init_async_generator)

        self.cbe_port_a.set_period(50)
        self.cbe_port_b.set_period(50)

        self.monoflop['a'].start()
        self.monoflop['b'].start()

    def stop(self):
        self.cbe_port_a.set_period(0)
        self.cbe_port_b.set_period(0)

        self.monoflop['a'].stop()
        self.monoflop['b'].stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIO16.DEVICE_IDENTIFIER

    def init_values(self, port, value, direction, config):
        for i in range(8):
            if direction & (1 << i):
                self.port_direction[port][i].setText('Input')

                if config & (1 << i):
                    self.port_config[port][i].setText('Pull-Up')
                else:
                    self.port_config[port][i].setText('Default')
            else:
                self.port_direction[port][i].setText('Output')
                self.port_config[port][i].setText('-')

            if value & (1 << i):
                self.port_value[port][i].setText('High')
            else:
                self.port_value[port][i].setText('Low')

        self.update_monoflop_ui_state()

    def update_monoflop_ui_state(self):
        port, pin = self.pin_box.currentText().lower()
        pin = int(pin)

        self.go_button.setEnabled(self.port_direction[port][pin].text().replace('&', '') == 'Output')

    def save_clicked(self):
        port, pin = self.pin_box.currentText().lower()
        pin = int(pin)
        direction = self.direction_box.currentText()[0].lower()

        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[port][pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull-Up'

        async_call(self.io.set_port_configuration, (port, 1 << pin, direction, value), None, self.increase_error_count)

        self.port_direction[port][pin].setText(self.direction_box.currentText())

        if direction == 'i':
            self.port_config[port][pin].setText(self.value_box.currentText())
        else:
            self.port_config[port][pin].setText('-')

        self.update_monoflop_ui_state()

    def cb_port(self, port, value):
        for i in range(8):
            if value & (1 << i):
                self.port_value[port][i].setText('High')
            else:
                self.port_value[port][i].setText('Low')

    def pin_changed(self, index):
        port, pin = self.pin_box.currentText().lower()
        pin = int(pin)

        if self.port_direction[port][pin].text().replace('&', '') == 'Input':
            direction_index = 0
        else:
            direction_index = 1

        self.direction_box.setCurrentIndex(direction_index)
        self.direction_changed(direction_index)

        self.monoflop_time_stack.setCurrentIndex(index)
        self.monoflop_value_stack.setCurrentIndex(index)

        self.update_monoflop_ui_state()

    def direction_changed(self, direction):
        port, pin = self.pin_box.currentText().lower()
        pin = int(pin)

        self.value_box.clear()

        if direction == 1:
            self.value_label.setText('Value:')
            self.value_box.addItem('High')
            self.value_box.addItem('Low')

            if self.port_value[port][pin].text().replace('&', '') == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_label.setText('Config:')
            self.value_box.addItem('Pull-Up')
            self.value_box.addItem('Default')

            if self.port_config[port][pin].text().replace('&', '') == 'Pull-Up':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)

        self.update_monoflop_ui_state()

    def debounce_save_clicked(self):
        debounce = int(self.debounce_edit.text())

        async_call(self.io.set_debounce_period, debounce, None, self.increase_error_count)

    def go_clicked(self):
        port, pin = self.pin_box.currentText().lower()
        pin = int(pin)

        self.monoflop[port].trigger(pin)

    def cb_value_change_by_monoflop(self, port, pin, value):
        if value:
            self.port_value[port][pin].setText('High')
        else:
            self.port_value[port][pin].setText('Low')

        self.port_config[port][pin].setText('-')

        selected_port, selected_pin = self.pin_box.currentText().lower()
        selected_pin = int(selected_pin)

        if port == selected_port and pin == selected_pin:
            if value:
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
