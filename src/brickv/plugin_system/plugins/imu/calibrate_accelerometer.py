# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_accelerometer.py: IMU Accelerometer Calibration implementation

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

from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSignal

from brickv.plugin_system.plugins.imu.ui_calibrate_accelerometer import Ui_calibrate_accelerometer

import time

class CalibrateAccelerometer(QWidget, Ui_calibrate_accelerometer):
    TYPE_ACC_GAIN = 0
    TYPE_ACC_BIAS = 1
    NUM_AVG = 5000
    qtcb_callback = pyqtSignal(int, int, int)
    
    def __init__(self, parent):
        QWidget.__init__(self)

        self.setupUi(self)
        
        self.parent = parent
        self.imu = parent.parent.imu
        
        self.set_default()
        self.start_button.pressed.connect(self.next_state)
        self.i = 0
        self.t = 0
        
        self.state = 0
        
        self.acc = [0, 0, 0]
        self.acc_sum = [0, 0, 0]
        
        self.acc_avg_p = [0, 0, 0]
        self.acc_avg_m = [0, 0, 0]
        
        self.acc_gain_mult = [0, 0, 0]
        self.acc_gain_div = [0, 0, 0]
        self.acc_bias = [0, 0, 0]
        
        self.qtcb_callback.connect(self.callback)
        
        
    def start(self):
        self.imu.register_callback(self.imu.CALLBACK_ACCELERATION, 
                                   self.qtcb_callback.emit)
        
    def stop(self):
        self.imu.set_acceleration_period(0)
        
    def calc(self, i):
        self.acc_bias[i] = ((1000  - self.acc_avg_p[i]) + 
                            (-1000 - self.acc_avg_m[i]))/2
                            
        self.acc_gain_mult[i] = 1000
        self.acc_gain_div[i] = self.acc_avg_p[i] + self.acc_bias[i]
        
        if i == 0:
            self.bias_x.setText(str(self.acc_bias[i]))
            self.gain_x.setText(str(self.acc_gain_mult[i]) + '/' + 
                                str(self.acc_gain_div[i]))
        elif i == 1:
            self.bias_y.setText(str(self.acc_bias[i]))
            self.gain_y.setText(str(self.acc_gain_mult[i]) + '/' + 
                                str(self.acc_gain_div[i]))
        elif i == 2:
            self.bias_z.setText(str(self.acc_bias[i]))
            self.gain_z.setText(str(self.acc_gain_mult[i]) + '/' + 
                                str(self.acc_gain_div[i]))
            
        
    def set_default(self):
        self.i = 0
        self.t = 0
        
        self.acc = [0, 0, 0]
        self.acc_sum = [0, 0, 0]
        
        self.acc_avg_p = [0, 0, 0]
        self.acc_avg_m = [0, 0, 0]
        
        self.acc_gain_mult = [0, 0, 0]
        self.acc_gain_div = [0, 0, 0]
        self.acc_bias = [0, 0, 0]
        
        text = """To calibrate the accelerometer you have to hold the \
IMU Brick in different orientations (you will be guided through the process). \
If you want to get good results you should fixate the IMU Brick on a leveled \
desk in every step, perhaps between two books or similar.

Note: As soon as you click "Start Calibration", the current calibration \
will be deleted. You can make a backup of the old calibration \
in the Im/Export tab."""
            
        self.text_label.setText(text)
        self.start_button.setText("Start Calibration")
        
    def next_state(self):
        self.state += 1
        if self.state == 14:
            self.state = 0
            
        if self.state == 0:
            gain = [self.acc_gain_mult[0], 
                    self.acc_gain_mult[1], 
                    self.acc_gain_mult[2], 
                    self.acc_gain_div[0],
                    self.acc_gain_div[1],
                    self.acc_gain_div[2],
                    0, 0, 0, 0]
            
            bias = [self.acc_bias[0],
                    self.acc_bias[1],
                    self.acc_bias[2],
                    0, 0, 0, 0, 0, 0, 0]
            
            self.imu.set_calibration(self.TYPE_ACC_GAIN, gain)
            self.imu.set_calibration(self.TYPE_ACC_BIAS, bias)
            self.parent.refresh_values()
            
            self.gain_x.setText("?")
            self.gain_y.setText("?")
            self.gain_z.setText("?")
            self.bias_x.setText("?")
            self.bias_y.setText("?")
            self.bias_z.setText("?")
            
            self.set_default()
            
        if self.state == 1:
            gain = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            bias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.imu.set_calibration(self.TYPE_ACC_GAIN, gain)
            self.imu.set_calibration(self.TYPE_ACC_BIAS, bias)
            self.parent.refresh_values()
            
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* Y-axis and Z-axis parallel to the ground 
* Positive X-axis points to the ground""")
            self.start_button.setText("Start X+ Calibration")
            
        if self.state == 2:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
            
        if self.state == 3:
            self.acc_avg_p[0] = self.acc_sum[0]/self.NUM_AVG
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* Y-axis and Z-axis parallel to the ground 
* Negative X-axis points to the ground""")
            self.start_button.setText("Start X- Calibration")
            
        if self.state == 4:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
            
        if self.state == 5:
            self.acc_avg_m[0] = self.acc_sum[0]/self.NUM_AVG
            self.calc(0)
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* X-axis and Z-axis parallel to the ground 
* Positive Y-axis points to the ground""")
            self.start_button.setText("Start Y+ Calibration")
            
        if self.state == 6:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
        if self.state == 7:
            self.acc_avg_p[1] = self.acc_sum[1]/self.NUM_AVG
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* X-axis and Z-axis parallel to the ground 
* Negative Y-axis points to the ground""")
            self.start_button.setText("Start Y- Calibration")
            
        if self.state == 8:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
            
        if self.state == 9:
            self.acc_avg_m[1] = self.acc_sum[1]/self.NUM_AVG
            self.calc(1)
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* X-axis and Y-axis parallel to the ground 
* Positive Z-axis points to the ground""")
            self.start_button.setText("Start Z+ Calibration")
            
        if self.state == 10:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
            
        if self.state == 11:
            self.acc_avg_p[2] = self.acc_sum[2]/self.NUM_AVG
            self.text_label.setText("""Please hold the IMU Brick in the \
following way:

* X-axis and Y-axis parallel to the ground 
* Negative Z-axis points to the ground""")
            self.start_button.setText("Start Z- Calibration")
            
        if self.state == 12:
            self.i = 0
            self.imu.set_acceleration_period(1)
            self.start_button.setEnabled(False)
            
        if self.state == 13:
            self.acc_avg_m[2] = self.acc_sum[2]/self.NUM_AVG
            self.calc(2)
            self.text_label.setText("""Press "Save Calibration" to upload \
the accelerometer calibration data to the IMU Brick""")
            self.start_button.setText("Save Calibration")
        
    def callback(self, acc_x, acc_y, acc_z):
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
        
        self.acc_sum[0] += acc_x
        self.acc_sum[1] += acc_y
        self.acc_sum[2] += acc_z
        
        self.i += 1
        
        if self.i == self.NUM_AVG:
            self.imu.set_acceleration_period(0)
            self.start_button.setEnabled(True)
            self.next_state()
            self.i = 0
