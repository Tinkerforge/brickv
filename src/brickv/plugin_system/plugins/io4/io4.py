# -*- coding: utf-8 -*-
"""
IO4 Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012, 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt5.QtWidgets import QDoubleSpinBox, QComboBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.io4.ui_io4 import Ui_IO4
from brickv.bindings.bricklet_io4 import BrickletIO4
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.monoflop import Monoflop

class IO4(PluginBase, Ui_IO4):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletIO4, *args)

        self.setupUi(self)

        self.io = self.device

        self.cbe_value = CallbackEmulator(self.io.get_value,
                                          None,
                                          self.cb_value,
                                          self.increase_error_count)

        self.port_value = [self.av0, self.av1, self.av2, self.av3]
        self.port_direction = [self.ad0, self.ad1, self.ad2, self.ad3]
        self.port_config = [self.ac0, self.ac1, self.ac2, self.ac3]
        self.port_time = [self.at0, self.at1, self.at2, self.at3]

        self.save_button.clicked.connect(self.save_clicked)
        self.pin_box.currentIndexChanged.connect(self.pin_changed)
        self.direction_box.currentIndexChanged.connect(self.direction_changed)
        self.debounce_save.clicked.connect(self.debounce_save_clicked)
        self.go_button.clicked.connect(self.go_clicked)

        self.monoflop_values = []
        self.monoflop_times = []

        for i in range(4):
            monoflop_value = QComboBox()
            monoflop_value.addItem('High', 1)
            monoflop_value.addItem('Low', 0)

            self.monoflop_values.append(monoflop_value)
            self.monoflop_value_stack.addWidget(monoflop_value)

            monoflop_time = QDoubleSpinBox()

            self.monoflop_times.append(monoflop_time)
            self.monoflop_time_stack.addWidget(monoflop_time)

        self.monoflop = Monoflop(self.io,
                                 [0, 1, 2, 3],
                                 self.monoflop_values,
                                 self.cb_value_change_by_monoflop,
                                 self.monoflop_times,
                                 self.port_time,
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

        async_call(self.io.get_value, None, get_port_async, self.increase_error_count)
        yield

        async_call(self.io.get_configuration, None, get_port_configuration_async, self.increase_error_count)
        yield

        self.init_values(self.init_value, self.init_dir, self.init_config)

        async_call(self.io.get_debounce_period, None, get_debounce_period_async, self.increase_error_count)

    def start(self):
        self.init_async_generator = self.init_async()
        next(self.init_async_generator)

        self.cbe_value.set_period(50)

        self.monoflop.start()

    def stop(self):
        self.cbe_value.set_period(0)

        self.monoflop.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIO4.DEVICE_IDENTIFIER

    def init_values(self, value, direction, config):
        for i in range(4):
            if direction & (1 << i):
                self.port_direction[i].setText('Input')

                if config & (1 << i):
                    self.port_config[i].setText('Pull-Up')
                else:
                    self.port_config[i].setText('Default')
            else:
                self.port_direction[i].setText('Output')
                self.port_config[i].setText('-')

            if value & (1 << i):
                self.port_value[i].setText('High')
            else:
                self.port_value[i].setText('Low')

        self.update_monoflop_ui_state()

    def update_monoflop_ui_state(self):
        pin = int(self.pin_box.currentText())

        self.go_button.setEnabled(self.port_direction[pin].text().replace('&', '') == 'Output')

    def save_clicked(self):
        pin = int(self.pin_box.currentText())
        direction = self.direction_box.currentText()[0].lower()

        if direction == 'o':
            value = self.value_box.currentText() == 'High'
            self.port_value[pin].setText(self.value_box.currentText())
        else:
            value = self.value_box.currentText() == 'Pull-Up'

        async_call(self.io.set_configuration, (1 << pin, direction, value), None, self.increase_error_count)

        self.port_direction[pin].setText(self.direction_box.currentText())

        if direction == 'i':
            self.port_config[pin].setText(self.value_box.currentText())
        else:
            self.port_config[pin].setText('-')

        self.update_monoflop_ui_state()

    def cb_value(self, value):
        for i in range(4):
            if value & (1 << i):
                self.port_value[i].setText('High')
            else:
                self.port_value[i].setText('Low')

    def pin_changed(self, pin):
        if self.port_direction[pin].text().replace('&', '') == 'Input':
            index = 0
        else:
            index = 1

        self.direction_box.setCurrentIndex(index)
        self.direction_changed(index)

        self.monoflop_time_stack.setCurrentIndex(pin)
        self.monoflop_value_stack.setCurrentIndex(pin)

        self.update_monoflop_ui_state()

    def direction_changed(self, direction):
        pin = int(self.pin_box.currentText())

        self.value_box.clear()

        if direction == 1:
            self.value_label.setText('Value:')
            self.value_box.addItem('High')
            self.value_box.addItem('Low')

            if self.port_value[pin].text().replace('&', '') == 'High':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
        else:
            self.value_label.setText('Config:')
            self.value_box.addItem('Pull-Up')
            self.value_box.addItem('Default')

            if self.port_config[pin].text().replace('&', '') == 'Pull-Up':
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)

        self.update_monoflop_ui_state()

    def debounce_save_clicked(self):
        debounce = int(self.debounce_edit.text())

        async_call(self.io.set_debounce_period, debounce, None, self.increase_error_count)

    def go_clicked(self):
        pin = int(self.pin_box.currentText())

        self.monoflop.trigger(pin)

    def cb_value_change_by_monoflop(self, pin, value):
        if value:
            self.port_value[pin].setText('High')
        else:
            self.port_value[pin].setText('Low')

        self.port_config[pin].setText('-')

        selected_pin = int(self.pin_box.currentText())

        if pin == selected_pin:
            if value:
                self.value_box.setCurrentIndex(0)
            else:
                self.value_box.setCurrentIndex(1)
