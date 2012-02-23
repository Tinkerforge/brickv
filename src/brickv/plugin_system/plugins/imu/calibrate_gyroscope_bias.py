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

from PyQt4.QtGui import QWidget
from PyQt4.QtCore import pyqtSignal, QTimer

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
        
        self.set_default()
        self.start_button.pressed.connect(self.next_state)
        self.i = 0
        self.t = 0
        
        self.state = 0
        self.temperature_raw = 0
        self.t_raw_start_low = 0
        self.t_raw_end_high = 0
        
        self.gyr_sum = [0, 0, 0]
        self.gyr_bias_low = [0, 0, 0]
        self.gyr_bias_high = [0, 0, 0]
        
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_temperature)
        self.update_timer.setInterval(1000)
        
        self.qtcb_callback.connect(self.callback)
        
    def start(self):
        self.update_temperature()
        self.update_timer.start()
        self.imu.register_callback(self.imu.CALLBACK_ANGULAR_VELOCITY, 
                                   self.qtcb_callback.emit)
        
    def stop(self):
        self.update_timer.stop()
        self.imu.set_angular_velocity_period(0)
        
    def update_temperature(self):
        self.temperature_raw = self.imu.get_imu_temperature()
        t_str = "%.2f" % (self.temperature_raw/100.0)
        
        if self.state < 2:
            self.t_low.setText(t_str)
        else:
            self.t_high.setText(t_str)
            
        
    def set_default(self):
        self.gyr_sum = [0, 0, 0]
        self.gyr_bias = [0, 0, 0]
        text = """For the gyroscope bias calibration the IMU Brick has \
to lie still for about 5 seconds. As soon as you press "Start Calibration" \
the calibration will begin.

Make sure that the IMU Brick lies absolutely still during the calibration. \
Don't make vibrations by walking around and don't type on your keyboard \
if possible place the IMU Brick on another desk. Even small vibrations can \
deteriorate this calibration significantly.

The gyroscope bias is highly dependent on the temperature, so you have to \
calibrate the bias two times with different temperatures. The first \
measurement should be with a low temperature and the second with a high one. \
The temperature difference should be at least 5%cC. If you have \
a temperature where the IMU Brick is mostly used, you should use this \
temperature for one of the sampling points.
""" % 0xB0 
            
        self.text_label.setText(text)
        self.start_button.setText("Start Calibration Low Temperature")
        
    def calc(self):
        if self.state == 2:
            for i in range(3):
                self.gyr_bias_low[i] = self.gyr_sum[i]/self.NUM_AVG
                                    
                if i == 0:
                    self.bias_low_x.setText(str(self.gyr_bias_low[i]))
                elif i == 1:
                    self.bias_low_y.setText(str(self.gyr_bias_low[i]))
                elif i == 2:
                    self.bias_low_z.setText(str(self.gyr_bias_low[i]))
        else:
            for i in range(3):
                self.gyr_bias_high[i] = self.gyr_sum[i]/self.NUM_AVG
                                    
                if i == 0:
                    self.bias_high_x.setText(str(self.gyr_bias_high[i]))
                elif i == 1:
                    self.bias_high_y.setText(str(self.gyr_bias_high[i]))
                elif i == 2:
                    self.bias_high_z.setText(str(self.gyr_bias_high[i]))
            
        
    def next_state(self):
        self.state += 1
        if self.state == 5:
            self.state = 0
            
        if self.state == 0:
            self.gyr_sum = [0, 0, 0]
            self.update_temperature()
            self.imu.set_angular_velocity_period(0)
            bias = [self.gyr_bias_low[0],
                    self.gyr_bias_low[1],
                    self.gyr_bias_low[2],
                    (self.t_raw_start_low + self.t_raw_end_low)/2, 
                    self.gyr_bias_high[0],
                    self.gyr_bias_high[1],
                    self.gyr_bias_high[2],
                    (self.t_raw_start_high + self.t_raw_end_high)/2, 
                    0, 0]
            
            self.imu.set_calibration(self.TYPE_GYR_BIAS, bias)
            self.parent.refresh_values()
            
            self.bias_low_x.setText("?")
            self.bias_low_y.setText("?")
            self.bias_low_z.setText("?")
            self.t_low.setText("?")
            self.bias_high_x.setText("?")
            self.bias_high_y.setText("?")
            self.bias_high_z.setText("?")
            self.t_high.setText("?")
            
            self.set_default()
            
        elif self.state == 1:
            self.update_timer.stop()
            self.t_raw_start_low = self.imu.get_imu_temperature()
            bias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.imu.set_calibration(self.TYPE_GYR_BIAS, bias)
            self.parent.refresh_values()
            
            self.imu.set_angular_velocity_period(1)
            self.text_label.setText("Waiting...")
            self.start_button.setEnabled(False)
            
        elif self.state == 2:
            self.t_raw_end_low = self.imu.get_imu_temperature()
            self.calc()
            self.update_temperature()
            self.update_timer.start()
            self.start_button.setText("Start Calibration High Temperature")
            self.text_label.setText("""Now wait for the temperature to rise. \
A temperature difference of at least 5%cC is recommended.

The calibration will again take 5 seconds and the IMU Brick needs to lie
absolutely still.""" % 0xB0)
        elif self.state == 3:
            self.update_timer.stop()
            self.t_raw_start_high = self.imu.get_imu_temperature()
            self.imu.set_angular_velocity_period(1)
            self.text_label.setText("Waiting...")
            self.start_button.setEnabled(False)
            pass
        if self.state == 4:
            self.t_raw_end_high = self.imu.get_imu_temperature()
            self.calc()
            self.text_label.setText("""Ready. To save the calibration \
press "Save Calibration" """)
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
        
        self.gyr_sum[0] -= gyr_x
        self.gyr_sum[1] -= gyr_y
        self.gyr_sum[2] -= gyr_z
        
        self.i += 1
        
        if self.i == self.NUM_AVG:
            self.imu.set_angular_velocity_period(0)
            self.start_button.setEnabled(True)
            self.next_state()
            self.i = 0