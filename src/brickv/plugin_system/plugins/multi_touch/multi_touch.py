# -*- coding: utf-8 -*-  
"""
Multi Touch Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_multi_touch import BrickletMultiTouch
from brickv.async_call import async_call

from brickv.plugin_system.plugins.multi_touch.ui_multi_touch import Ui_MultiTouch

from PyQt4.QtCore import pyqtSignal
    
class MultiTouch(PluginBase, Ui_MultiTouch):
    qtcb_touch_state = pyqtSignal(int)
    
    def __init__(self, *args):
        PluginBase.__init__(self, 'Multi Touch Bricklet', BrickletMultiTouch, *args)

        self.setupUi(self)

        self.mt = self.device
        
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
            self.mt_label_12, 
        ]
        
        for label in self.mt_labels:
            label.setStyleSheet("QLabel { background-color : black; }");
        
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
            
        self.button_recalibrate.pressed.connect(self.recalibrate_pressed)
        
    def recalibrate_pressed(self):
        value = self.sensitivity_spinbox.value()
        self.mt.set_electrode_sensitivity(value)
        self.mt.recalibrate()
        
    def state_changed(self, state):
        enabled_electrodes = 0
        for i in range(13):
            if self.cbs[i].isChecked():
                enabled_electrodes |= 1 << i
        
        self.mt.set_electrode_config(enabled_electrodes)
        
    def cb_touch_state(self, state):
        for i in range(13):
            if state & (1 << i):
                self.mt_labels[i].setStyleSheet("QLabel { background-color : green; }");
            else:
                self.mt_labels[i].setStyleSheet("QLabel { background-color : black; }");
                
    def cb_electrode_config(self, enabled_electrodes):
        for i in range(13):
            if enabled_electrodes & (1 << i):
                self.cbs[i].setChecked(True)
            else:
                self.cbs[i].setChecked(False)
                
    def cb_electrode_sensitivity(self, sensitivity):
        self.sensitivity_spinbox.setValue(sensitivity)

    def start(self):
        async_call(self.mt.get_electrode_sensitivity, None, self.cb_electrode_sensitivity, self.increase_error_count)
        async_call(self.mt.get_electrode_config, None, self.cb_electrode_config, self.increase_error_count)
        
    def stop(self):
        pass

    def destroy(self):
        self.destroy_ui()

    def get_url_part(self):
        return 'multi_touch'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletMultiTouch.DEVICE_IDENTIFIER
