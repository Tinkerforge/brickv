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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_dual_button import BrickletDualButton
from brickv.async_call import async_call

from brickv.plugin_system.plugins.dual_button.ui_dual_button import Ui_DualButton
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
        PluginBase.__init__(self, ipcon, uid, 'Dual Button Bricklet', version, BrickletDualButton)
        
        self.setupUi(self)

        self.button = self.device
        
        self.qtcb_state_changed.connect(self.cb_state_changed)
        self.button.register_callback(self.button.CALLBACK_STATE_CHANGED,
                                      self.qtcb_state_changed.emit)
        
        self.led_r = DualButton.OFF
        self.led_l = DualButton.OFF
        self.button_r = DualButton.RELEASED
        self.button_l = DualButton.RELEASED
        
        self.button_led_on_button_r.pressed.connect(self.on_button_r_pressed)
        self.button_led_on_button_l.pressed.connect(self.on_button_l_pressed)
        self.button_led_off_button_r.pressed.connect(self.off_button_r_pressed)
        self.button_led_off_button_l.pressed.connect(self.off_button_l_pressed)
        self.button_toggle_button_r.pressed.connect(self.toggle_button_r_pressed)
        self.button_toggle_button_l.pressed.connect(self.toggle_button_l_pressed)
        
        self.count = 0
        
    def on_button_l_pressed(self):
        self.led_l = DualButton.ON
        self.button.set_led_state(DualButton.ON, self.led_r)
        self.update_buttons()
        
    def on_button_r_pressed(self):
        self.led_r = DualButton.ON
        self.button.set_led_state(self.led_l, DualButton.ON)
        self.update_buttons()
        
    def off_button_l_pressed(self):
        self.led_l = DualButton.OFF
        self.button.set_led_state(DualButton.OFF, self.led_r)
        self.update_buttons()
    
    def off_button_r_pressed(self):
        self.led_r = DualButton.OFF
        self.button.set_led_state(self.led_l, DualButton.OFF)
        self.update_buttons()
        
    def toggle_button_l_pressed(self):
        self.led_l = DualButton.AT_OFF
        self.button.set_led_state(DualButton.AT_OFF, self.led_r)
        self.update_buttons()
    
    def toggle_button_r_pressed(self):
        self.led_r = DualButton.AT_OFF
        self.button.set_led_state(self.led_l, DualButton.AT_OFF)
        self.update_buttons()
        
    def update_buttons(self):
        if self.led_r == DualButton.ON:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(False)
            self.button_led_off_button_r.setEnabled(True)
        elif self.led_r == DualButton.OFF:
            self.button_toggle_button_r.setEnabled(True)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(False)
        elif self.led_r in (DualButton.AT_OFF, DualButton.AT_ON):
            self.button_toggle_button_r.setEnabled(False)
            self.button_led_on_button_r.setEnabled(True)
            self.button_led_off_button_r.setEnabled(True)
            
        if self.led_l == DualButton.ON:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(False)
            self.button_led_off_button_l.setEnabled(True)
        elif self.led_l == DualButton.OFF:
            self.button_toggle_button_l.setEnabled(True)
            self.button_led_on_button_l.setEnabled(True)
            self.button_led_off_button_l.setEnabled(False)
        elif self.led_l in (DualButton.AT_OFF, DualButton.AT_ON):
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
    
    def get_button_state_async(self, button):
        self.button_l, self.button_r = button
        led_text_button_l = ''
        led_text_button_r = ''
        
        if self.led_l in (DualButton.ON, DualButton.AT_ON):
            led_text_button_l = ', LED On'
        else:
            led_text_button_l = ', LED Off'
            
        if self.led_r in (DualButton.ON, DualButton.AT_ON):
            led_text_button_r = ', LED On'
        else:
            led_text_button_r = ', LED Off'
            
        if self.button_l == DualButton.RELEASED:
            self.label_status_button_l.setText('Released' + led_text_button_l)
        else:
            self.label_status_button_l.setText('Pressed' + led_text_button_l)
            
        if self.button_r == DualButton.RELEASED:
            self.label_status_button_r.setText('Released' + led_text_button_r)
        else:
            self.label_status_button_r.setText('Pressed' + led_text_button_r)

    def start(self):
        async_call(self.button.get_led_state, None, self.get_led_state_async, self.increase_error_count)
        async_call(self.button.get_button_state, None, self.get_button_state_async, self.increase_error_count)
        
    def stop(self):
        pass

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'dual_button'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletDualButton.DEVICE_IDENTIFIER
