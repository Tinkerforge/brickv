# -*- coding: utf-8 -*-
"""
Multi Touch V2 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

multi_touch_v2.py: Multi Touch 2.0 Plugin Implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.multi_touch_v2.ui_multi_touch_v2 import Ui_MultiTouchV2
from brickv.bindings.bricklet_multi_touch_v2 import BrickletMultiTouchV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class MultiTouchV2(COMCUPluginBase, Ui_MultiTouchV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletMultiTouchV2, *args)

        self.setupUi(self)

        self.mt = self.device
        self.cbe_state = CallbackEmulator(self.mt.get_touch_state, self.cb_touch_state, self.increase_error_count)


        self.mt_labels = [
            self.mt_label_0,
            self.mt_label_1,
            self.mt_label_2,
            self.mt_label_3,
            self.mt_label_4,
            self.mt_label_5,
            self.mt_label_6,
            self.mt_label_7,
            self.mt_label_8,
            self.mt_label_9,
            self.mt_label_10,
            self.mt_label_11,
            self.mt_label_12,
        ]

        for label in self.mt_labels:
            label.setStyleSheet("QLabel { background-color : black; }")

        self.cbs = [
            self.cb_0,
            self.cb_1,
            self.cb_2,
            self.cb_3,
            self.cb_4,
            self.cb_5,
            self.cb_6,
            self.cb_7,
            self.cb_8,
            self.cb_9,
            self.cb_10,
            self.cb_11,
            self.cb_12,
        ]

        for cb in self.cbs:
            cb.stateChanged.connect(self.state_changed)

        self.button_recalibrate.clicked.connect(self.recalibrate_clicked)

    def recalibrate_clicked(self):
        value = self.sensitivity_spinbox.value()
        self.mt.set_electrode_sensitivity(value)
        self.mt.recalibrate()

    def state_changed(self, _state):
        enabled_electrodes = [False]*13
        for i in range(len(enabled_electrodes)):
            if self.cbs[i].isChecked():
                enabled_electrodes[i] = True

        self.mt.set_electrode_config(enabled_electrodes)

    def cb_touch_state(self, state):
        for i in range(len(state)):
            if state[i]:
                self.mt_labels[i].setStyleSheet("QLabel { background-color : green; }")
            else:
                self.mt_labels[i].setStyleSheet("QLabel { background-color : black; }")

    def cb_electrode_config(self, enabled_electrodes):
        for i in range(len(enabled_electrodes)):
            if enabled_electrodes[i]:
                self.cbs[i].setChecked(True)
            else:
                self.cbs[i].setChecked(False)

    def cb_electrode_sensitivity(self, sensitivity):
        self.sensitivity_spinbox.setValue(sensitivity)

    def start(self):
        async_call(self.mt.get_electrode_sensitivity, None, self.cb_electrode_sensitivity, self.increase_error_count)
        async_call(self.mt.get_electrode_config, None, self.cb_electrode_config, self.increase_error_count)
        async_call(self.mt.get_touch_state, None, self.cb_touch_state, self.increase_error_count)
        self.cbe_state.set_period(100)

    def stop(self):
        self.cbe_state.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMultiTouchV2.DEVICE_IDENTIFIER
