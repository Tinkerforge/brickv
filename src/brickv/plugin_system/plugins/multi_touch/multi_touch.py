# -*- coding: utf-8 -*-  
"""
Multi Touch Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>

multi_touch.py: Multi Touch Plugin Implementation

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
from bindings.bricklet_multi_touch import BrickletMultiTouch
from async_call import async_call

from ui_multi_touch import Ui_MultiTouch

from PyQt4.QtGui import QLabel, QVBoxLayout
from PyQt4.QtCore import pyqtSignal
    
class MultiTouch(PluginBase, Ui_MultiTouch):
    qtcb_touch_state = pyqtSignal(int)
    
    def __init__(self, ipcon, uid, version):
        PluginBase.__init__(self, ipcon, uid, 'Multi Touch Bricklet', version)
        
        self.setupUi(self)

        self.mt = BrickletMultiTouch(uid, ipcon)
        
        self.qtcb_touch_state.connect(self.cb_touch_state)
        self.mt.register_callback(self.mt.CALLBACK_TOUCH_STATE,
                                  self.qtcb_touch_state.emit)
        
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
        ]
        
        for label in self.mt_labels:
            label.setStyleSheet("QLabel { background-color : black; }");
        
    def cb_touch_state(self, state):
        for i in range(12):
            if state & (1 << i):
                self.mt_labels[i].setStyleSheet("QLabel { background-color : green; }");
            else:
                self.mt_labels[i].setStyleSheet("QLabel { background-color : black; }");
        print bin(state)

    def start(self):
        pass
        
    def stop(self):
        pass

    def get_url_part(self):
        return 'multi_touch'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMultiTouch.DEVICE_IDENTIFIER