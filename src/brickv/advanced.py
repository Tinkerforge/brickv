# -*- coding: utf-8 -*-  
"""
brickv (Brick Viewer) 
Copyright (C) 2011 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012 Bastian Nordmeyer <bastian@tinkerforge.com>
Copyright (C) 2012 Matthias Bolte <matthias@tinkerforge.com>

advanced.py: GUI for advanced features

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

from ui_advanced import Ui_widget_advanced
import time

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QFrame, QFileDialog, QMessageBox

import sys

class AdvancedWindow(QFrame, Ui_widget_advanced):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)

        self.button_calibrate.setEnabled(False)
        
        self.ipcon = parent.ipcon
        self.button_calibrate.pressed.connect(self.calibrate_pressed)
        self.combo_brick.currentIndexChanged.connect(self.brick_changed)
        self.check_enable_calibration.stateChanged.connect(self.enable_calibration_changed)
        self.devices = []

    def calibrate_pressed(self):
        self.ipcon.adc_calibrate(self.current_device(), 
                                 str(self.combo_port.currentText()).lower())
        
        self.update_calibration()
    
    def current_device_and_port(self):
        return (self.current_device(), 
                str(self.combo_port.currentText()).lower())

    def current_device(self):
        return self.devices[self.combo_brick.currentIndex()]

    def update_calibration(self, device = None):
        if device == None:
            device = self.current_device()
            
        offset, gain = self.ipcon.get_adc_calibration(device)
        
        self.label_offset.setText(str(offset))
        self.label_gain.setText(str(gain))
        
    def brick_changed(self, index):
        if len(self.devices) <= index:
            return
        
        self.update_calibration(self.devices[index])

    def enable_calibration_changed(self, state):
        if state == Qt.Unchecked:
            self.button_calibrate.setEnabled(False) 
        else:
            self.button_calibrate.setEnabled(True)
