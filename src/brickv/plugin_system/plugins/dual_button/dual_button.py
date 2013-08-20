# -*- coding: utf-8 -*-  
"""
Dual Button Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

dual_button.py: Dual Button Plugin Implementation

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
from bindings.bricklet_dual_button import BrickletDualButton
from async_call import async_call

from ui_dual_button import Ui_DualButton
from PyQt4.QtCore import pyqtSignal
    
class DualButton(PluginBase, Ui_DualButton):
    qtcb_state_changed = pyqtSignal(int, int, int, int)
    
    AT_ON = 0
    AT_OFF = 1
    ON = 2
    OFF = 3
    
    PRESSED = 0
    RELEASED = 1
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Dual Button Bricklet', version)
        
        self.setupUi(self)

        self.button = BrickletDualButton(uid, ipcon)
        
        self.qtcb_state_changed.connect(self.cb_state_changed)
        self.button.register_callback(self.button.CALLBACK_STATE_CHANGED,
                                      self.qtcb_state_changed.emit)
        
        self.led1 = DualButton.OFF
        self.led2 = DualButton.OFF
        self.button1 = DualButton.RELEASED
        self.button2 = DualButton.RELEASED
        
        self.button_led_on_b1.pressed.connect(self.on_b1_pressed)
        self.button_led_on_b2.pressed.connect(self.on_b2_pressed)
        self.button_led_off_b1.pressed.connect(self.off_b1_pressed)
        self.button_led_off_b2.pressed.connect(self.off_b2_pressed)
        self.button_toggle_b1.pressed.connect(self.toggle_b1_pressed)
        self.button_toggle_b2.pressed.connect(self.toggle_b2_pressed)
        
    def on_b1_pressed(self):
        self.led1 = DualButton.ON
        self.button.set_led_state(DualButton.ON, self.led2)
        self.update_buttons()
    
    def on_b2_pressed(self):
        self.led2 = DualButton.ON
        self.button.set_led_state(self.led1, DualButton.ON)
        self.update_buttons()
    
    def off_b1_pressed(self):
        self.led1 = DualButton.OFF
        self.button.set_led_state(DualButton.OFF, self.led2)
        self.update_buttons()
    
    def off_b2_pressed(self):
        self.led2 = DualButton.OFF
        self.button.set_led_state(self.led1, DualButton.OFF)
        self.update_buttons()
    
    def toggle_b1_pressed(self):
        self.led1 = DualButton.AT_OFF
        self.button.set_led_state(DualButton.AT_OFF, self.led2)
        self.update_buttons()
    
    def toggle_b2_pressed(self):
        self.led2 = DualButton.AT_OFF
        self.button.set_led_state(self.led1, DualButton.AT_OFF)
        self.update_buttons()
        
    def update_buttons(self):
        if self.led1 == DualButton.ON:
            self.button_toggle_b1.setEnabled(True)
            self.button_led_on_b1.setEnabled(False)
            self.button_led_off_b1.setEnabled(True)
        elif self.led1 == DualButton.OFF:
            self.button_toggle_b1.setEnabled(True)
            self.button_led_on_b1.setEnabled(True)
            self.button_led_off_b1.setEnabled(False)
        elif self.led1 == DualButton.AT_OFF:
            self.button_toggle_b1.setEnabled(False)
            self.button_led_on_b1.setEnabled(True)
            self.button_led_off_b1.setEnabled(True)
            
        if self.led2 == DualButton.ON:
            self.button_toggle_b2.setEnabled(True)
            self.button_led_on_b2.setEnabled(False)
            self.button_led_off_b2.setEnabled(True)
        elif self.led2 == DualButton.OFF:
            self.button_toggle_b2.setEnabled(True)
            self.button_led_on_b2.setEnabled(True)
            self.button_led_off_b2.setEnabled(False)
        elif self.led2 == DualButton.AT_OFF:
            self.button_toggle_b2.setEnabled(False)
            self.button_led_on_b2.setEnabled(True)
            self.button_led_off_b2.setEnabled(True)
            
    def cb_state_changed(self, button1, button2, led1, led2):
        self.get_led_state_async((led1, led2))
        self.get_button_state_async((button1, button2))
        
        self.update_buttons()
    
    def get_led_state_async(self, led):
        self.led1, self.led2 = led
    
    def get_button_state_async(self, button):
        self.button1, self.button2 = button
        led_text_b1 = ''
        led_text_b2 = ''
        
        if self.led1 in (DualButton.ON, DualButton.AT_ON):
            led_text_b1 = ', LED On'
        else:
            led_text_b1 = ', LED Off'
            
        if self.led2 in (DualButton.ON, DualButton.AT_ON):
            led_text_b2 = ', LED On'
        else:
            led_text_b2 = ', LED Off'
            
        if self.button1 == DualButton.RELEASED:
            self.label_status_b1.setText('Released' + led_text_b1)
        else:
            self.label_status_b1.setText('Pressed' + led_text_b1)
            
        if self.button2 == DualButton.RELEASED:
            self.label_status_b2.setText('Released' + led_text_b2)
        else:
            self.label_status_b2.setText('Pressed' + led_text_b2)

    def start(self):
        async_call(self.button.get_led_state, None, self.get_led_state_async, self.increase_error_count)
        async_call(self.button.get_button_state, None, self.get_button_state_async, self.increase_error_count)
        
    def stop(self):
        pass

    def get_url_part(self):
        return 'dual_button'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualButton.DEVICE_IDENTIFIER