# -*- coding: utf-8 -*-  
"""
Remote Switch Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

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

from plugin_system.plugin_base import PluginBase
from bindings.bricklet_remote_switch import BrickletRemoteSwitch
from async_call import async_call

from ui_remote_switch import Ui_RemoteSwitch

from PyQt4.QtCore import pyqtSignal

class RemoteSwitch(PluginBase, Ui_RemoteSwitch):
    qtcb_switching_done = pyqtSignal()
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Remote Switch Bricklet', version)
        
        self.setupUi(self)

        self.rs = BrickletRemoteSwitch(uid, ipcon)
        
        self.qtcb_switching_done.connect(self.cb_switching_done)
        self.rs.register_callback(self.rs.CALLBACK_SWITCHING_DONE,
                                  self.qtcb_switching_done.emit)
        
        self.h_check = (self.h_check_a, self.h_check_b, self.h_check_c, self.h_check_d, self.h_check_e)
        self.r_check = (self.r_check_a, self.r_check_b, self.r_check_c, self.r_check_d, self.r_check_e)
        
        self.button_switch.pressed.connect(self.button_pressed)

    def start(self):
        pass
        
    def stop(self):
        pass
    
    def button_pressed(self):
        self.button_switch.setEnabled(False)
        self.button_switch.setText("Switching...")
        
        repeats = self.spinbox_repeats.value()
        self.rs.set_repeats(repeats)
        
        house_code = 0
        for i in range(5):
            if self.h_check[i].isChecked():
                house_code |= (1 << i)
                
        receiver_code = 0
        for i in range(5):
            if self.r_check[i].isChecked():
                receiver_code |= (1 << i)
        
        switch_to = self.combo_onoff.currentIndex()
        self.rs.switch_socket(house_code, receiver_code, switch_to)
            
    
    def cb_switching_done(self):
        self.button_switch.setEnabled(True)
        self.button_switch.setText("Switch Socket")

    def get_url_part(self):
        return 'remote_switch'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletRemoteSwitch.DEVICE_IDENTIFIER