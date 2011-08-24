# -*- coding: utf-8 -*-  
"""
Dual Relay Plugin
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>

dual_relay.py: Dual Relay Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt4.QtCore import Qt
        
import bricklet_dual_relay
        
class DualRelay(PluginBase):
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        
        self.dr = bricklet_dual_relay.DualRelay(self.uid)
        self.ipcon.add_device(self.dr)
        
        dr1_label = QLabel("Relay 1:")
        self.dr1_button = QPushButton("Off")
        dr1_layout = QHBoxLayout()
        dr1_layout.addStretch()
        dr1_layout.addWidget(dr1_label)
        dr1_layout.addWidget(self.dr1_button)
        dr1_layout.addStretch()
        
        dr2_label = QLabel("Relay 2:")
        self.dr2_button = QPushButton("Off")
        dr2_layout = QHBoxLayout()
        dr2_layout.addStretch()
        dr2_layout.addWidget(dr2_label)
        dr2_layout.addWidget(self.dr2_button)
        dr2_layout.addStretch()
        
        self.dr1_button.pressed.connect(self.dr1_pressed)
        self.dr2_button.pressed.connect(self.dr2_pressed)
        
        layout = QVBoxLayout(self)
        layout.addLayout(dr1_layout)
        layout.addLayout(dr2_layout)
        layout.addStretch()

    def start(self):
        pass
        
    def stop(self):
        pass

    @staticmethod
    def has_name(name):
        return 'Dual Relay Bricklet' in name 
    
    def get_state(self):
        return (self.dr1_button.text() == 'On', self.dr2_button.text() == 'On')
    
    def dr1_pressed(self):
        if self.dr1_button.text() == 'On':
            self.dr1_button.setText('Off')
        else:
            self.dr1_button.setText('On')
        
        dr1, dr2 = self.get_state()
        
        self.dr.set_state(dr1, dr2)
        
    def dr2_pressed(self):
        if self.dr2_button.text() == 'On':
            self.dr2_button.setText('Off')
        else:
            self.dr2_button.setText('On')
        
        dr1, dr2 = self.get_state()
        
        self.dr.set_state(dr1, dr2)