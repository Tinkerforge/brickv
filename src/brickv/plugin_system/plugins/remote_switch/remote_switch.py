# -*- coding: utf-8 -*-
"""
Remote Switch Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

remote_switch.py: Remote Switch Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.remote_switch.ui_remote_switch import Ui_RemoteSwitch
from brickv.bindings.bricklet_remote_switch import BrickletRemoteSwitch

class RemoteSwitch(PluginBase, Ui_RemoteSwitch):
    qtcb_switching_done = pyqtSignal()

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletRemoteSwitch, *args)

        self.setupUi(self)

        self.rs = self.device

        self.has_more_types = self.firmware_version >= (2, 0, 1)

        self.qtcb_switching_done.connect(self.cb_switching_done)
        self.rs.register_callback(self.rs.CALLBACK_SWITCHING_DONE,
                                  self.qtcb_switching_done.emit)

        self.h_check = (self.h_check_a, self.h_check_b, self.h_check_c, self.h_check_d, self.h_check_e)
        self.r_check = (self.r_check_a, self.r_check_b, self.r_check_c, self.r_check_d, self.r_check_e)
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

        self.type_a_widgets = [self.groupbox_house, self.groupbox_receiver, self.button_switch_on, self.button_switch_off]
        self.type_b_widgets = [self.widget_address, self.widget_unit, self.button_switch_on, self.button_switch_off]
        self.type_b_dim_widgets = [self.widget_dim_value, self.widget_address, self.widget_unit, self.button_dim]
        self.type_c_widgets = [self.widget_system_code, self.widget_device_code, self.button_switch_on, self.button_switch_off]
        self.type_widgets = (self.type_a_widgets, self.type_b_widgets, self.type_b_dim_widgets, self.type_c_widgets)

        if self.has_more_types:
            self.label_hint.setVisible(False)
        else:
            self.combo_type.clear()
            self.combo_type.addItem('A Switch')

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
            self.spinbox_unit.setEnabled(False)
        else:
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

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    def dim_clicked(self):
        self.button_dim.setEnabled(False)
        self.button_dim.setText("Dimming...")

        repeats = self.spinbox_repeats.value()
        self.rs.set_repeats(repeats)

        if self.combo_type.currentIndex() == 2:
            address = self.spinbox_address.value()
            unit = self.spinbox_unit.value()
            if self.checkbox_switchall.isChecked():
                unit = 255

            dim_value = self.spinbox_dim_value.value()

            self.rs.dim_socket_b(address, unit, dim_value)

    def button_clicked(self, switch_to):
        self.button_switch_on.setEnabled(False)
        self.button_switch_on.setText("Switching...")
        self.button_switch_off.setEnabled(False)
        self.button_switch_off.setText("Switching...")

        repeats = self.spinbox_repeats.value()
        self.rs.set_repeats(repeats)

        if self.combo_type.currentText() == 'A Switch':
            house_code = self.spinbox_house.value()
            receiver_code = self.spinbox_receiver.value()
            self.rs.switch_socket(house_code, receiver_code, switch_to)
        elif self.combo_type.currentText() == 'B Switch':
            address = self.spinbox_address.value()
            unit = self.spinbox_unit.value()
            if self.checkbox_switchall.isChecked():
                unit = 255

            self.rs.switch_socket_b(address, unit, switch_to)
        elif self.combo_type.currentText() == 'C Switch':
            system_code = self.combo_system_code.currentText()[0]
            device_code = self.spinbox_device_code.value()
            self.rs.switch_socket_c(system_code, device_code, switch_to)

    def cb_switching_done(self):
        self.button_switch_on.setEnabled(True)
        self.button_switch_on.setText("Switch On")
        self.button_switch_off.setEnabled(True)
        self.button_switch_off.setText("Switch Off")
        self.button_dim.setEnabled(True)
        self.button_dim.setText("Dim")

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRemoteSwitch.DEVICE_IDENTIFIER
