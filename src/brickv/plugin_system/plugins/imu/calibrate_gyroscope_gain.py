# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_gyroscope_gain.py: IMU Gyroscope Gain Calibration implementation

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

from ui_calibrate_gyroscope_gain import Ui_calibrate_gyroscope_gain

import time

class CalibrateGyroscopeGain(QWidget, Ui_calibrate_gyroscope_gain):
    TYPE_GYR_GAIN = 4
    NUM_AVG = 1000
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
        
        self.gyr = [0, 0, 0]
        self.gyr_sum = [0, 0, 0]
        
        self.gyr_gain_mult = [0, 0, 0]
        self.gyr_gain_div = [0, 0, 0]
        
        self.qtcb_callback.connect(self.callback)
        
    def start(self):
        self.imu.register_callback(self.imu.CALLBACK_ANGULAR_VELOCITY, 
                                   self.qtcb_callback.emit)
        
    def stop(self):
        self.imu.set_angular_velocity_period(0)
        
    def calc(self, i):
        self.gyr_gain_mult[i] = 1000
        self.gyr_gain_div[i] = self.gyr[i]
        
        if i == 0:
            self.gain_x.setText(str(self.gyr_gain_mult[i]) + '/' + 
                                str(self.gyr_gain_div[i]))
        elif i == 1:
            self.gain_y.setText(str(self.gyr_gain_mult[i]) + '/' + 
                                str(self.gyr_gain_div[i]))
        elif i == 2:
            self.gain_z.setText(str(self.gyr_gain_mult[i]) + '/' + 
                                str(self.gyr_gain_div[i]))
            
        
    def next_state(self):
        self.state += 1
        if self.state == 8:
            self.state = 0
            
        if self.state == 0:
            gain = [self.gyr_gain_mult[0], 
                    self.gyr_gain_mult[1], 
                    self.gyr_gain_mult[2], 
                    self.gyr_gain_div[0],
                    self.gyr_gain_div[1],
                    self.gyr_gain_div[2],
                    0, 0, 0, 0]
            
            self.imu.set_calibration(self.TYPE_GYR_GAIN, gain)
            self.parent.refresh_values()
            
            self.gain_x.setText("?")
            self.gain_y.setText("?")
            self.gain_z.setText("?")
            
            self.text_label.setText("Gyroscope gain Calibration...")
            self.start_button.setText("Start Calibration")
        if self.state == 1:
            gain = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            self.imu.set_calibration(self.TYPE_GYR_GAIN, gain)
            self.parent.refresh_values()
            
            self.text_label.setText("Hold IMU in certain way X...")
            self.start_button.setText("Start X Calibration")
        if self.state == 2:
            self.i = 0
            self.imu.set_angular_velocity_period(1)
            self.start_button.setEnabled(False)
        if self.state == 3:
            self.gyr[0] = self.gyr_sum[0]/self.NUM_AVG
            self.calc(0)
            self.text_label.setText("Hold IMU in certain way Y...")
            self.start_button.setText("Start Y Calibration")
        if self.state == 4:
            self.i = 0
            self.imu.set_angular_velocity_period(1)
            self.start_button.setEnabled(False)
        if self.state == 5:
            self.gyr[1] = self.gyr_sum[1]/self.NUM_AVG
            self.calc(1)
            self.text_label.setText("Hold IMU in certain way Z...")
            self.start_button.setText("Start Z Calibration")
        if self.state == 6:
            self.i = 0
            self.imu.set_angular_velocity_period(1)
            self.start_button.setEnabled(False)
        if self.state == 7:
            self.gyr[2] = self.gyr_sum[2]/self.NUM_AVG
            self.calc(2)
            self.text_label.setText("Save calibration")
            self.start_button.setText("Save Calibration")
        
    def callback(self, gyr_x, gyr_y, gyr_z):
        if self.i == 0:
            self.t = time.time()
            self.gyr_sum = [0, 0, 0]
        
        if not self.start_button.isEnabled():
            self.text_label.setText("Calibrating: " + 
                                    str(self.i) + 
                                    '/' + 
                                    str(self.NUM_AVG))
        else:
            return
        
        self.gyr_sum[0] += gyr_x
        self.gyr_sum[1] += gyr_y
        self.gyr_sum[2] += gyr_z
        
        self.i += 1
        
        if self.i == self.NUM_AVG:
            print time.time() - self.t 
            self.imu.set_angular_velocity_period(0)
            self.start_button.setEnabled(True)
            self.next_state()
            self.i = 0