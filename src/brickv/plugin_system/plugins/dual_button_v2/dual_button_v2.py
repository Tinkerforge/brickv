# -*- coding: utf-8 -*-
"""
Dual Button Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

dual_button_v2.py: Dual Button V2 Plugin Implementation

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

from PyQt4.QtCore import pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.dual_button_v2.ui_dual_button_v2 import Ui_DualButtonV2
from brickv.bindings.bricklet_dual_button_v2 import BrickletDualButtonV2
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class DualButtonV2(COMCUPluginBase, Ui_DualButtonV2):
    qtcb_state_changed = pyqtSignal(int, int, int, int)

    AT_ON = 0
    AT_OFF = 1
    ON = 2
    OFF = 3

    PRESSED = 0
    RELEASED = 1

    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletDualButtonV2, *args)

        self.setupUi(self)

        self.button = self.device

        self.cbe_button_state = CallbackEmulator(self.button.get_button_state,
                                                 self.cb_button_state,
                                                 self.increase_error_count)
        self.led_r = DualButtonV2.OFF
        self.led_l = DualButtonV2.OFF
        self.button_r = DualButtonV2.RELEASED
        self.button_l = DualButtonV2.RELEASED

        self.button_led_on_button_r.clicked.connect(self.on_button_r_clicked)
        self.button_led_on_button_l.clicked.connect(self.on_button_l_clicked)
        self.button_led_off_button_r.clicked.connect(self.off_button_r_clicked)
        self.button_led_off_button_l.clicked.connect(self.off_button_l_clicked)
        self.button_toggle_button_r.clicked.connect(self.toggle_button_r_clicked)
        self.button_toggle_button_l.clicked.connect(self.toggle_button_l_clicked)

        self.count = 0

    def cb_button_state(self, state):
        self.button_l, self.button_r = state 
        led_text_button_l = ''
        led_text_button_r = ''

        if self.led_l in (DualButtonV2.ON, DualButtonV2.AT_ON):
            led_text_button_l = ', LED On'
        else:
            led_text_button_l = ', LED Off'

        if self.led_r in (DualButtonV2.ON, DualButtonV2.AT_ON):
            led_text_button_r = ', LED On'
        else:
            led_text_button_r = ', LED Off'

        if self.button_l == DualButtonV2.RELEASED:
            self.label_status_button_l.setText('Released' + led_text_button_l)
        else:
            self.label_status_button_l.setText('Pressed' + led_text_button_l)

        if self.button_r == DualButtonV2.RELEASED:
            self.label_status_button_r.setText('Released' + led_text_button_r)
        else:
            self.label_status_button_r.setText('Pressed' + led_text_button_r)

    def on_button_l_clicked(self):
        self.led_l = DualButtonV2.ON
        self.button.set_led_state(DualButtonV2.ON, self.led_r)
        self.update_buttons()

    def on_button_r_clicked(self):
        self.led_r = DualButtonV2.ON
        self.button.set_led_state(self.led_l, DualButtonV2.ON)
        self.update_buttons()

    def off_button_l_clicked(self):
        self.led_l = DualButtonV2.OFF
        self.button.set_led_state(DualButtonV2.OFF, self.led_r)
        self.update_buttons()

    def off_button_r_clicked(self):
        self.led_r = DualButtonV2.OFF
        self.button.set_led_state(self.led_l, DualButtonV2.OFF)
        self.update_buttons()

    def toggle_button_l_clicked(self):
        self.led_l = DualButtonV2.AT_OFF
        self.button.set_led_state(DualButtonV2.AT_OFF, self.led_r)
        self.update_buttons()

    def toggle_button_r_clicked(self):
        self.led_r = DualButtonV2.AT_OFF
        self.button.set_led_state(self.led_l, DualButtonV2.AT_OFF)
        self.update_buttons()

    def update_buttons(self):
        if self.led_r == DualButtonV2.ON:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(False)
            self.button_led_off_button_r.setEnabled(True)
        elif self.led_r == DualButtonV2.OFF:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(False)
        elif self.led_r in (DualButtonV2.AT_OFF, DualButtonV2.AT_ON):
            self.button_toggle_button_r.setEnabled(False)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(True)

        if self.led_l == DualButtonV2.ON:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(False)
            self.button_led_off_button_l.setEnabled(True)
        elif self.led_l == DualButtonV2.OFF:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(True)
            self.button_led_off_button_l.setEnabled(False)
        elif self.led_l in (DualButtonV2.AT_OFF, DualButtonV2.AT_ON):
            self.button_toggle_button_l.setEnabled(False)
            self.button_led_on_button_l.setEnabled(True)
            self.button_led_off_button_l.setEnabled(True)

    def cb_state_changed(self, button_l, button_r, led_l, led_r):
        self.count += 1
        self.get_led_state_async((led_l, led_r))
        self.get_button_state_async((button_l, button_r))

    def get_led_state_async(self, led):
        self.led_l, self.led_r = led

        self.update_buttons()

    def start(self):
        async_call(self.button.get_led_state, None, self.get_led_state_async, self.increase_error_count)
        self.cbe_button_state.set_period(100)

    def stop(self):
        self.cbe_button_state.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualButtonV2.DEVICE_IDENTIFIER
