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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.dual_button_v2.ui_dual_button_v2 import Ui_DualButtonV2
from brickv.bindings.bricklet_dual_button_v2 import BrickletDualButtonV2
from brickv.callback_emulator import CallbackEmulator

class DualButtonV2(COMCUPluginBase, Ui_DualButtonV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletDualButtonV2, *args)

        self.setupUi(self)

        self.button = self.device

        self.cbe_button_state = CallbackEmulator(self.button.get_button_state,
                                                 None,
                                                 self.cb_button_state,
                                                 self.increase_error_count,
                                                 expand_result_tuple_for_callback=True)

        self.cbe_led_state = CallbackEmulator(self.button.get_led_state,
                                              None,
                                              self.cb_led_state,
                                              self.increase_error_count,
                                              expand_result_tuple_for_callback=True)

        self.led_r = BrickletDualButtonV2.LED_STATE_OFF
        self.led_l = BrickletDualButtonV2.LED_STATE_OFF
        self.button_r = BrickletDualButtonV2.BUTTON_STATE_RELEASED
        self.button_l = BrickletDualButtonV2.BUTTON_STATE_RELEASED

        self.button_led_on_button_r.clicked.connect(self.on_button_r_clicked)
        self.button_led_on_button_l.clicked.connect(self.on_button_l_clicked)
        self.button_led_off_button_r.clicked.connect(self.off_button_r_clicked)
        self.button_led_off_button_l.clicked.connect(self.off_button_l_clicked)
        self.button_toggle_button_r.clicked.connect(self.toggle_button_r_clicked)
        self.button_toggle_button_l.clicked.connect(self.toggle_button_l_clicked)

        self.count = 0

    def cb_button_state(self, button_l, button_r):
        self.button_l = button_l
        self.button_r = button_r
        self.update_labels()

    def update_labels(self):
        led_text_button_l = ''
        led_text_button_r = ''

        if self.led_l in (BrickletDualButtonV2.LED_STATE_ON, BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_ON):
            led_text_button_l = ', LED On'
        else:
            led_text_button_l = ', LED Off'

        if self.led_r in (BrickletDualButtonV2.LED_STATE_ON, BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_ON):
            led_text_button_r = ', LED On'
        else:
            led_text_button_r = ', LED Off'

        if self.button_l == BrickletDualButtonV2.BUTTON_STATE_RELEASED:
            self.label_status_button_l.setText('Released' + led_text_button_l)
        else:
            self.label_status_button_l.setText('Pressed' + led_text_button_l)

        if self.button_r == BrickletDualButtonV2.BUTTON_STATE_RELEASED:
            self.label_status_button_r.setText('Released' + led_text_button_r)
        else:
            self.label_status_button_r.setText('Pressed' + led_text_button_r)

        self.update_buttons()

    def on_button_l_clicked(self):
        self.led_l = BrickletDualButtonV2.LED_STATE_ON
        self.button.set_led_state(BrickletDualButtonV2.LED_STATE_ON, self.led_r)
        self.update_buttons()
        self.update_labels()

    def on_button_r_clicked(self):
        self.led_r = BrickletDualButtonV2.LED_STATE_ON
        self.button.set_led_state(self.led_l, BrickletDualButtonV2.LED_STATE_ON)
        self.update_buttons()
        self.update_labels()

    def off_button_l_clicked(self):
        self.led_l = BrickletDualButtonV2.LED_STATE_OFF
        self.button.set_led_state(BrickletDualButtonV2.LED_STATE_OFF, self.led_r)
        self.update_buttons()
        self.update_labels()

    def off_button_r_clicked(self):
        self.led_r = BrickletDualButtonV2.LED_STATE_OFF
        self.button.set_led_state(self.led_l, BrickletDualButtonV2.LED_STATE_OFF)
        self.update_buttons()
        self.update_labels()

    def toggle_button_l_clicked(self):
        self.led_l = BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF
        self.button.set_led_state(BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF, self.led_r)
        self.update_buttons()
        self.update_labels()

    def toggle_button_r_clicked(self):
        self.led_r = BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF
        self.button.set_led_state(self.led_l, BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF)
        self.update_buttons()
        self.update_labels()

    def update_buttons(self):
        if self.led_r == BrickletDualButtonV2.LED_STATE_ON:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(False)
            self.button_led_off_button_r.setEnabled(True)
        elif self.led_r == BrickletDualButtonV2.LED_STATE_OFF:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(False)
        elif self.led_r in (BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_ON, BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF):
            self.button_toggle_button_r.setEnabled(False)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(True)

        if self.led_l == BrickletDualButtonV2.LED_STATE_ON:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(False)
            self.button_led_off_button_l.setEnabled(True)
        elif self.led_l == BrickletDualButtonV2.LED_STATE_OFF:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(True)
            self.button_led_off_button_l.setEnabled(False)
        elif self.led_l in (BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_ON, BrickletDualButtonV2.LED_STATE_AUTO_TOGGLE_OFF):
            self.button_toggle_button_l.setEnabled(False)
            self.button_led_on_button_l.setEnabled(True)
            self.button_led_off_button_l.setEnabled(True)

    def cb_led_state(self, led_l, led_r):
        self.led_l = led_l
        self.led_r = led_r

        self.cb_button_state(self.button_l, self.button_r)

    def start(self):
        self.cbe_button_state.set_period(200)
        self.cbe_led_state.set_period(200)

    def stop(self):
        self.cbe_button_state.set_period(0)
        self.cbe_led_state.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualButtonV2.DEVICE_IDENTIFIER
