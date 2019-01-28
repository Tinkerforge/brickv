# -*- coding: utf-8 -*-
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_magnetometer.py: IMU Magnetometer Calibration implementation

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

from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from brickv.plugin_system.plugins.imu.ui_calibrate_magnetometer import Ui_calibrate_magnetometer

class CalibrateMagnetometer(QWidget, Ui_calibrate_magnetometer):
    TYPE_MAG_GAIN = 2
    TYPE_MAG_BIAS = 3
    qtcb_callback = pyqtSignal(int, int, int)

    def __init__(self, parent):
        QWidget.__init__(self)

        self.setupUi(self)

        self.parent = parent
        self.imu = parent.parent.imu

        self.set_default()
        self.start_button.clicked.connect(self.next_state)

        self.state = 0

        self.mag_max = [0, 0, 0]
        self.mag_min = [0, 0, 0]

        self.acc_gain_mult = [0, 0, 0]
        self.acc_gain_div = [0, 0, 0]
        self.acc_bias = [0, 0, 0]

        self.qtcb_callback.connect(self.callback)

    def start(self):
        self.imu.register_callback(self.imu.CALLBACK_MAGNETIC_FIELD,
                                   self.qtcb_callback.emit)

    def stop(self):
        self.imu.set_magnetic_field_period(0)

    def set_default(self):
        self.mag_max = [0, 0, 0]
        self.mag_min = [0, 0, 0]

        self.acc_gain_mult = [0, 0, 0]
        self.acc_gain_div = [0, 0, 0]
        self.acc_bias = [0, 0, 0]

        text = """The magnetometer calibration should take place in the \
same location where the IMU Brick is used later on. Especially if the \
IMU Brick is used near a motor or any other device with a strong magnetic \
field, you have to calibrate it "in place".

Note: As soon as you click "Start Calibration", the current calibration \
will be deleted. You can make a backup of the old calibration \
in the Im/Export tab."""

        self.text_label.setText(text)
        self.start_button.setText("Start Calibration")

    def calc(self):
        for i in range(3):
            self.acc_bias[i] = ((500  - self.mag_max[i]) +
                                (-500 - self.mag_min[i]))/2

            self.acc_gain_mult[i] = 500
            self.acc_gain_div[i] = self.mag_max[i] + self.acc_bias[i]

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


    def next_state(self):
        self.state += 1
        if self.state == 2:
            self.state = 0

        if self.state == 0:
            self.imu.set_magnetic_field_period(0)
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

            self.imu.set_calibration(self.TYPE_MAG_GAIN, gain)
            self.imu.set_calibration(self.TYPE_MAG_BIAS, bias)
            self.parent.refresh_values()

            self.gain_x.setText("?")
            self.gain_y.setText("?")
            self.gain_z.setText("?")
            self.bias_x.setText("?")
            self.bias_y.setText("?")
            self.bias_z.setText("?")


            self.set_default()

        elif self.state == 1:
            gain = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
            bias = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            self.imu.set_calibration(self.TYPE_MAG_GAIN, gain)
            self.imu.set_calibration(self.TYPE_MAG_BIAS, bias)
            self.parent.refresh_values()

            self.imu.set_magnetic_field_period(1)
            self.text_label.setText("""Now fling your IMU Brick around until \
the values shown above stop changing. Make sure that you reach every \
possible orientation at least once.

If you press "Ready" the magnetometer calibration will be uploaded""")
            self.start_button.setText("Ready")

    def callback(self, mag_x, mag_y, mag_z):
        if self.state == 0:
            return

        if self.mag_max[0] < mag_x:
            self.mag_max[0] = mag_x
        elif self.mag_min[0] > mag_x:
            self.mag_min[0] = mag_x

        if self.mag_max[1] < mag_y:
            self.mag_max[1] = mag_y
        elif self.mag_min[1] > mag_y:
            self.mag_min[1] = mag_y

        if self.mag_max[2] < mag_z:
            self.mag_max[2] = mag_z
        elif self.mag_min[2] > mag_z:
            self.mag_min[2] = mag_z

        self.calc()
