# -*- coding: utf-8 -*-  
"""
Master Plugin
Copyright (C) 2010 Olaf Lüke <olaf@tinkerforge.com>

master.py: Master Plugin implementation

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

#import logging

from plugin_system.plugin_base import PluginBase

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QVBoxLayout, QLabel
from ui_master import Ui_Master

import brick_master

class Master(PluginBase, Ui_Master):
    def __init__ (self, ipcon, uid):
        PluginBase.__init__(self, ipcon, uid)
        self.setupUi(self)

        self.master = brick_master.Master(self.uid)
        self.device = self.master
        self.ipcon.add_device(self.master)
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

    def start(self):
        self.update_timer.start(100)

    def stop(self):
        self.update_timer.stop()
    
    @staticmethod
    def has_name(name):
        return 'Master Brick' in name
        
    def update_data(self):
        sv = self.master.get_stack_voltage()
        sc = self.master.get_stack_current()
        self.stack_voltage_update(sv)
        self.stack_current_update(sc)
        
    def stack_voltage_update(self, sv):
        sv_str = "%gV"  % round(sv/1000.0, 1)
        self.stack_voltage_label.setText(sv_str)
        
    def stack_current_update(self, sc):
        if sc < 999:
            sc_str = "%gmA" % sc
        else:
            sc_str = "%gA" % round(sc/1000.0, 1)   
        self.stack_current_label.setText(sc_str)