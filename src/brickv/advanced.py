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

from PyQt4.QtCore import pyqtSignal, Qt, QTimer
from PyQt4.QtGui import QApplication, QFrame, QFileDialog, QMessageBox

import sys

NO_BRICK = 'No Brick found'

class AdvancedWindow(QFrame, Ui_widget_advanced):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)
        self.setupUi(self)

        self.button_calibrate.setEnabled(False)
        
        self.parent = parent
        self.button_calibrate.pressed.connect(self.calibrate_pressed)
        self.combo_brick.currentIndexChanged.connect(self.brick_changed)
        self.check_enable_calibration.stateChanged.connect(self.enable_calibration_changed)

        self.set_devices([])

    def set_devices(self, devices):
        self.devices = []
        self.combo_brick.clear()

        for device in devices:
            self.devices.append(device[1])
            self.combo_brick.addItem(device[0])

        if self.combo_brick.count() == 0:
            self.combo_brick.addItem(NO_BRICK)

        self.update_calibration()
        self.update_ui_state()

    def calibrate_pressed(self):
        self.parent.ipcon.adc_calibrate(self.current_device(),
                                        str(self.combo_port.currentText()).lower())
        
        self.update_calibration()

    def current_device(self):
        index = self.combo_brick.currentIndex()
        if index < 0 or len(self.devices) == 0:
            return None
        else:
            return self.devices[index]

    def update_calibration(self):
        device = self.current_device()

        if device is None:
            self.label_offset.setText('-')
            self.label_gain.setText('-')
        else:
            def slot():
                offset, gain = self.parent.ipcon.get_adc_calibration(device)
                self.label_offset.setText(str(offset))
                self.label_gain.setText(str(gain))
            QTimer.singleShot(0, slot)
        
    def brick_changed(self, index):
        self.update_calibration()

    def enable_calibration_changed(self, state):
        self.button_calibrate.setEnabled(state == Qt.Checked)

    def update_ui_state(self):
        enabled = len(self.devices) > 0

        self.combo_brick.setEnabled(enabled)
        self.check_enable_calibration.setEnabled(enabled)
        self.button_calibrate.setEnabled(enabled and self.check_enable_calibration.isChecked())
