# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_gyroscope_bias.py: IMU Gyroscope Bias Calibration implementation

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

from PyQt4.QtGui import QWidget, QFrame, QMessageBox
from PyQt4.QtCore import QTimer, Qt, pyqtSignal

from ui_calibrate_gyroscope_bias import Ui_calibrate_gyroscope_bias

import time

class CalibrateGyroscopeBias(QWidget, Ui_calibrate_gyroscope_bias):
    TYPE_GYR_BIAS = 5
    NUM_AVG = 5000
    qtcb_callback = pyqtSignal(int, int, int)
    
    def __init__(self, parent):
        QWidget.__init__(self)
        self.setupUi(self)
        
        self.parent = parent
        self.imu = parent.parent.imu
        
        self.start_button.pressed.connect(self.next_state)
        self.i = 0
        self.t = 0
        
        self.state = 0
        
        self.gyr_sum = [0, 0, 0]
        self.gyr_bias = [0, 0, 0]
        
        self.qtcb_callback.connect(self.callback)
        
    def start(self):
        self.imu.register_callback(self.imu.CALLBACK_ANGULAR_VELOCITY, 
                                   self.qtcb_callback.emit)
        
    def stop(self):
        self.imu.set_angular_velocity_period(0)
        
    def calc(self):
        for i in range(3):
            self.gyr_bias[i] = self.gyr_sum[i]/self.NUM_AVG
                                
            if i == 0:
                self.bias_x.setText(str(self.gyr_bias[i]))
            elif i == 1:
                self.bias_y.setText(str(self.gyr_bias[i]))
            elif i == 2:
                self.bias_z.setText(str(self.gyr_bias[i]))
            
        
    def next_state(self):
        self.state += 1
        if self.state == 3:
            self.state = 0
            
        if self.state == 0:
            self.imu.set_angular_velocity_period(0)
            bias = [self.gyr_bias[0],
                    self.gyr_bias[1],
                    self.gyr_bias[2],
                    0, 0, 0, 0, 0, 0, 0]
            
            self.imu.set_calibration(self.TYPE_GYR_BIAS, bias)
            self.parent.refresh_values()
            
            self.bias_x.setText("?")
            self.bias_y.setText("?")
            self.bias_z.setText("?")
            
            self.text_label.setText("Gyroscope Gain Calibration..., lay still")
            self.start_button.setText("Start Calibration")
            
        elif self.state == 1:
            bias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.imu.set_calibration(self.TYPE_GYR_BIAS, bias)
            self.parent.refresh_values()
            
            self.imu.set_angular_velocity_period(1)
            self.text_label.setText("Waiting...")
            self.start_button.setEnabled(False)
            
        if self.state == 2:
            self.calc()
            self.text_label.setText("Ready")
            self.start_button.setText("Save Calibration")
        
    def callback(self, gyr_x, gyr_y, gyr_z):
        if self.i == 0:
            self.t = time.time()
            self.acc_sum = [0, 0, 0]
            
        if not self.start_button.isEnabled():
            self.text_label.setText("Calibrating: " + 
                                    str(self.i) + 
                                    '/' + 
                                    str(self.NUM_AVG))
        else:
            return
        
        self.gyr_sum[0] -= gyr_x
        self.gyr_sum[1] -= gyr_y
        self.gyr_sum[2] -= gyr_z
        
        self.i += 1
        
        if self.i == self.NUM_AVG:
            print time.time() - self.t 
            self.imu.set_angular_velocity_period(0)
            self.start_button.setEnabled(True)
            self.next_state()
            self.i = 0