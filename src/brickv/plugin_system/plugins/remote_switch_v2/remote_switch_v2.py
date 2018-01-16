# -*- coding: utf-8 -*-
"""
Remote Switch V2 Plugin
Copyright (C) 2017 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

remote_switch_v2.py: Remote Switch V2 Plugin Implementation

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

from PyQt4.QtCore import pyqtSignal, QTimer
from PyQt4.QtGui import QTextCursor

from brickv.async_call import async_call
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.remote_switch_v2.ui_remote_switch_v2 import Ui_RemoteSwitchV2
from brickv.bindings.bricklet_remote_switch_v2 import BrickletRemoteSwitchV2

class RemoteSwitchV2(COMCUPluginBase, Ui_RemoteSwitchV2):
    qtcb_switching_done = pyqtSignal()

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletRemoteSwitchV2, *args)

        self.setupUi(self)

        self.rs2 = self.device

        self.qtcb_switching_done.connect(self.cb_switching_done)
        self.rs2.register_callback(self.rs2.CALLBACK_SWITCHING_DONE,
                                   self.qtcb_switching_done.emit)

        self.h_check = (self.h_check_a,
                        self.h_check_b,
                        self.h_check_c,
                        self.h_check_d,
                        self.h_check_e)

        self.r_check = (self.r_check_a,
                        self.r_check_b,
                        self.r_check_c,
                        self.r_check_d,
                        self.r_check_e)

        for h in self.h_check:
            h.stateChanged.connect(self.h_check_state_changed)

        for r in self.r_check:
            r.stateChanged.connect(self.r_check_state_changed)

        self.checkbox_switchall.stateChanged.connect(self.switchall_state_changed)
        self.spinbox_house.valueChanged.connect(self.house_value_changed)
        self.spinbox_receiver.valueChanged.connect(self.receiver_value_changed)
        self.combo_type.currentIndexChanged.connect(self.type_index_changed)

        self.spinbox_dim_value.valueChanged.connect(self.spinbox_dim_value_changed)
        self.slider_dim_value.valueChanged.connect(self.slider_dim_value_changed)

        self.button_switch_on.clicked.connect(lambda: self.button_clicked(1))
        self.button_switch_off.clicked.connect(lambda: self.button_clicked(0))
        self.button_dim.clicked.connect(self.dim_clicked)

        self.combo_remote_type.currentIndexChanged.connect(self.remote_type_changed)
        self.button_remote_input_clear.clicked.connect(self.plaintextedit_remote_input.clear)

        self.current_remote_type = None
        self.timer_get_remote_input = QTimer()
        self.timer_get_remote_input.timeout.connect(self.timeout_get_remote_input)
        self.timer_get_remote_input.setInterval(50)

        self.last_remote_input = {
                                  'a': {
                                    'house_code': None,
                                    'receiver_code': None,
                                    'switch_to': None,
                                    'repeats': None
                                  },
                                  'b': {
                                    'address': None,
                                    'unit': None,
                                    'switch_to': None,
                                    'dim_value': None,
                                    'repeats': None
                                  },
                                  'c': {
                                    'system_code': None,
                                    'device_code': None,
                                    'switch_to': None,
                                    'repeats': None
                                  },
                                 }

        self.type_a_widgets = [self.label_house_code,
                               self.h_check_a,
                               self.h_check_b,
                               self.h_check_c,
                               self.h_check_d,
                               self.h_check_e,
                               self.spinbox_house,
                               self.label_receiver_code,
                               self.r_check_a,
                               self.r_check_b,
                               self.r_check_c,
                               self.r_check_d,
                               self.r_check_e,
                               self.spinbox_receiver,
                               self.button_switch_on,
                               self.button_switch_off]

        self.type_b_widgets = [self.label_address,
                               self.spinbox_address,
                               self.label_unit,
                               self.spinbox_unit,
                               self.checkbox_switchall,
                               self.button_switch_on,
                               self.button_switch_off]

        self.type_b_dim_widgets = [self.label_address,
                                   self.spinbox_address,
                                   self.label_unit,
                                   self.spinbox_unit,
                                   self.checkbox_switchall,
                                   self.label_dim,
                                   self.spinbox_dim_value,
                                   self.slider_dim_value,
                                   self.button_dim]

        self.type_c_widgets = [self.label_system_code,
                               self.combo_system_code,
                               self.label_device_code,
                               self.spinbox_device_code,
                               self.button_switch_on,
                               self.button_switch_off]

        self.type_widgets = (self.type_a_widgets,
                             self.type_b_widgets,
                             self.type_b_dim_widgets,
                             self.type_c_widgets)

        self.type_index_changed(0)

    def spinbox_dim_value_changed(self, value):
        self.slider_dim_value.setValue(value)

    def slider_dim_value_changed(self, value):
        self.spinbox_dim_value.setValue(value)

    def type_index_changed(self, index):
        for i in range(len(self.type_widgets)):
            if i != index:
                for w in self.type_widgets[i]:
                    w.setVisible(False)

        for w in self.type_widgets[index]:
            w.setVisible(True)

    def house_value_changed(self, state):
        for i in range(5):
            if state & (1 << i):
                self.h_check[i].setChecked(True)
            else:
                self.h_check[i].setChecked(False)

    def receiver_value_changed(self, state):
        for i in range(5):
            if state & (1 << i):
                self.r_check[i].setChecked(True)
            else:
                self.r_check[i].setChecked(False)

    def switchall_state_changed(self, state):
        if self.checkbox_switchall.isChecked():
            self.spinbox_address.setEnabled(False)
            self.spinbox_unit.setEnabled(False)
        else:
            self.spinbox_address.setEnabled(True)
            self.spinbox_unit.setEnabled(True)

    def h_check_state_changed(self, state):
        house_code = 0
        for i in range(5):
            if self.h_check[i].isChecked():
                house_code |= (1 << i)

        self.spinbox_house.setValue(house_code)

    def r_check_state_changed(self, state):
        receiver_code = 0
        for i in range(5):
            if self.r_check[i].isChecked():
                receiver_code |= (1 << i)

        self.spinbox_receiver.setValue(receiver_code)

    def get_remote_configuration_async(self, remote_config):
        self.current_remote_type = remote_config.remote_type

        self.spinbox_remote_minimum_repeats.setValue(remote_config.minimum_repeats)

        if remote_config.remote_type == self.rs2.REMOTE_TYPE_A:
            self.combo_remote_type.setCurrentIndex(self.rs2.REMOTE_TYPE_A)
        elif remote_config.remote_type == self.rs2.REMOTE_TYPE_B:
            self.combo_remote_type.setCurrentIndex(self.rs2.REMOTE_TYPE_B)
        elif remote_config.remote_type == self.rs2.REMOTE_TYPE_C:
            self.combo_remote_type.setCurrentIndex(self.rs2.REMOTE_TYPE_C)

    def start(self):
        self.timer_get_remote_input.start()
        async_call(self.rs2.get_remote_configuration,
                   None,
                   self.get_remote_configuration_async,
                   self.increase_error_count)

    def stop(self):
        pass
        self.timer_get_remote_input.stop()

    def destroy(self):
        pass

    def dim_clicked(self):
        self.button_dim.setEnabled(False)
        self.button_dim.setText("Dimming...")

        repeats = self.spinbox_repeats.value()
        self.rs2.set_repeats(repeats)

        if self.combo_type.currentIndex() == 2:
            address = self.spinbox_address.value()
            unit = self.spinbox_unit.value()
            if self.checkbox_switchall.isChecked():
                address = 0
                unit = 255

            dim_value = self.spinbox_dim_value.value()

            self.rs2.dim_socket_b(address, unit, dim_value)

    def remote_type_changed(self, index):
        self.current_remote_type = index
        remote_config = self.rs2.get_remote_configuration()

        self.rs2.set_remote_configuration(index,
                                          remote_config.minimum_repeats,
                                          remote_config.callback_enabled)

        remote_config = self.rs2.get_remote_configuration()

    def get_remote_status_a_async(self, remote_config):
        if remote_config.repeats <= self.spinbox_remote_minimum_repeats.value():
            return

        if self.last_remote_input['a']['house_code'] == remote_config.house_code and \
           self.last_remote_input['a']['receiver_code'] == remote_config.receiver_code and \
           self.last_remote_input['a']['switch_to'] == remote_config.switch_to and \
           self.last_remote_input['a']['repeats'] == remote_config.repeats:
                return

        if self.last_remote_input['a']['house_code'] == None and \
           self.last_remote_input['a']['receiver_code'] == None and \
           self.last_remote_input['a']['switch_to'] == None and \
           self.last_remote_input['a']['repeats'] == None:
                self.last_remote_input['a']['house_code'] = remote_config.house_code
                self.last_remote_input['a']['receiver_code'] = remote_config.receiver_code
                self.last_remote_input['a']['switch_to'] = remote_config.switch_to
                self.last_remote_input['a']['repeats'] = remote_config.repeats

                return

        self.last_remote_input['a']['house_code'] = remote_config.house_code
        self.last_remote_input['a']['receiver_code'] = remote_config.receiver_code
        self.last_remote_input['a']['switch_to'] = remote_config.switch_to
        self.last_remote_input['a']['repeats'] = remote_config.repeats

        remote_input = '''Remote Type - A:
House code = {house_code}
Receiver code = {receiver_code}
Switch to = {switch_to}
Reapeats = {repeats}

'''.format(house_code=remote_config.house_code,
           receiver_code=remote_config.receiver_code,
           switch_to=remote_config.switch_to,
           repeats=remote_config.repeats)

        self.plaintextedit_remote_input.appendPlainText(remote_input)
        self.plaintextedit_remote_input.moveCursor(QTextCursor.End)

    def get_remote_status_b_async(self, remote_config):
        if remote_config.repeats <= self.spinbox_remote_minimum_repeats.value():
            return

        if self.last_remote_input['b']['address'] == remote_config.address and \
           self.last_remote_input['b']['unit'] == remote_config.unit and \
           self.last_remote_input['b']['switch_to'] == remote_config.switch_to and \
           self.last_remote_input['b']['dim_value'] == remote_config.dim_value and \
           self.last_remote_input['b']['repeats'] == remote_config.repeats:
                return

        if self.last_remote_input['b']['address'] == None and \
           self.last_remote_input['b']['unit'] == None and \
           self.last_remote_input['b']['switch_to'] == None and \
           self.last_remote_input['b']['dim_value'] == None and \
           self.last_remote_input['b']['repeats'] == None:
                self.last_remote_input['b']['address'] = remote_config.address
                self.last_remote_input['b']['unit'] = remote_config.unit
                self.last_remote_input['b']['switch_to'] = remote_config.switch_to
                self.last_remote_input['b']['dim_value'] = remote_config.dim_value
                self.last_remote_input['b']['repeats'] = remote_config.repeats

                return

        self.last_remote_input['b']['address'] = remote_config.address
        self.last_remote_input['b']['unit'] = remote_config.unit
        self.last_remote_input['b']['switch_to'] = remote_config.switch_to
        self.last_remote_input['b']['dim_value'] = remote_config.dim_value
        self.last_remote_input['b']['repeats'] = remote_config.repeats

        remote_input = '''Remote Type - B:
Address = {address}
Unit = {unit}_async
Switch to = {switch_to}
Dim value = {dim_value}
Repeats = {repeats}

'''.format(address=remote_config.address,
           unit=remote_config.unit,
           switch_to=remote_config.switch_to,
           dim_value=remote_config.dim_value,
           repeats=remote_config.repeats)

        self.plaintextedit_remote_input.appendPlainText(remote_input)
        self.plaintextedit_remote_input.moveCursor(QTextCursor.End)

    def get_remote_status_c_async(self, remote_config):
        if remote_config.repeats <= self.spinbox_remote_minimum_repeats.value():
            return

        if self.last_remote_input['c']['system_code'] == remote_config.system_code and \
           self.last_remote_input['c']['device_code'] == remote_config.device_code and \
           self.last_remote_input['c']['switch_to'] == remote_config.switch_to and \
           self.last_remote_input['c']['repeats'] == remote_config.repeats:
                return

        if self.last_remote_input['c']['system_code'] == None and \
           self.last_remote_input['c']['device_code'] == None and \
           self.last_remote_input['c']['switch_to'] == None and \
           self.last_remote_input['c']['repeats'] == None:
                self.last_remote_input['c']['system_code'] = remote_config.system_code
                self.last_remote_input['c']['device_code'] = remote_config.device_code
                self.last_remote_input['c']['switch_to'] = remote_config.switch_to
                self.last_remote_input['c']['repeats'] = remote_config.repeats

                return

        self.last_remote_input['c']['system_code'] = remote_config.system_code
        self.last_remote_input['c']['device_code'] = remote_config.device_code
        self.last_remote_input['c']['switch_to'] = remote_config.switch_to
        self.last_remote_input['c']['repeats'] = remote_config.repeats

        remote_input = '''Remote Type - C:
System code = {system_code}
Device code = {device_code}
Switch to = {switch_to}
Reapeats = {repeats}

'''.format(system_code=remote_config.system_code,
           device_code=remote_config.device_code,
           switch_to=remote_config.switch_to,
           repeats=remote_config.repeats)

        self.plaintextedit_remote_input.appendPlainText(remote_input)
        self.plaintextedit_remote_input.moveCursor(QTextCursor.End)

    def timeout_get_remote_input(self):
        if self.current_remote_type == self.rs2.REMOTE_TYPE_A:
            async_call(self.rs2.get_remote_status_a,
                       None,
                       self.get_remote_status_a_async,
                       self.increase_error_count)
        elif self.current_remote_type == self.rs2.REMOTE_TYPE_B:
            async_call(self.rs2.get_remote_status_b,
                       None,
                       self.get_remote_status_b_async,
                       self.increase_error_count)
        elif self.current_remote_type == self.rs2.REMOTE_TYPE_C:
            async_call(self.rs2.get_remote_status_c,
                       None,
                       self.get_remote_status_c_async,
                       self.increase_error_count)

    def button_clicked(self, switch_to):
        self.button_switch_on.setEnabled(False)
        self.button_switch_on.setText("Switching...")
        self.button_switch_off.setEnabled(False)
        self.button_switch_off.setText("Switching...")

        repeats = self.spinbox_repeats.value()
        self.rs2.set_repeats(repeats)

        if self.combo_type.currentText() == 'A Switch':
            house_code = self.spinbox_house.value()
            receiver_code = self.spinbox_receiver.value()
            self.rs2.switch_socket_a(house_code, receiver_code, switch_to)
        elif self.combo_type.currentText() == 'B Switch':
            address = self.spinbox_address.value()
            unit = self.spinbox_unit.value()

            if self.checkbox_switchall.isChecked():
                address = 0
                unit = 255

            self.rs2.switch_socket_b(address, unit, switch_to)
        elif self.combo_type.currentText() == 'C Switch':
            system_code = self.combo_system_code.currentText()[0]
            device_code = self.spinbox_device_code.value()
            self.rs2.switch_socket_c(system_code, device_code, switch_to)

    def cb_switching_done(self):
        self.button_switch_on.setEnabled(True)
        self.button_switch_on.setText("Switch On")
        self.button_switch_off.setEnabled(True)
        self.button_switch_off.setText("Switch Off")
        self.button_dim.setEnabled(True)
        self.button_dim.setText("Dim")

    def get_url_part(self):
        return 'remote_switch_v2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRemoteSwitchV2.DEVICE_IDENTIFIER
