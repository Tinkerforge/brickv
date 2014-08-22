# -*- coding: utf-8 -*-  
"""
IMU Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

calibrate_window.py: IMU calibration implementation

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

from brickv.plugin_system.plugins.imu.ui_calibrate import Ui_widget_calibrate

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QFrame, QTabWidget

from brickv.plugin_system.plugins.imu.calibrate_accelerometer import CalibrateAccelerometer
from brickv.plugin_system.plugins.imu.calibrate_magnetometer import CalibrateMagnetometer
from brickv.plugin_system.plugins.imu.calibrate_gyroscope_bias import CalibrateGyroscopeBias
from brickv.plugin_system.plugins.imu.calibrate_gyroscope_gain import CalibrateGyroscopeGain
from brickv.plugin_system.plugins.imu.calibrate_temperature import CalibrateTemperature
from brickv.plugin_system.plugins.imu.calibrate_import_export import CalibrateImportExport

class CalibrateWindow(QFrame, Ui_widget_calibrate):
    TYPE_ACC_GAIN = 0
    TYPE_ACC_BIAS = 1
    TYPE_MAG_GAIN = 2
    TYPE_MAG_BIAS = 3
    TYPE_GYR_GAIN = 4
    TYPE_GYR_BIAS = 5

    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)

        self.setupUi(self)

        self.setWindowTitle("IMU Calibration")
        
        self.parent = parent
        self.ipcon = parent.ipcon
        self.imu = parent.imu
        
        self.cal_acc = CalibrateAccelerometer(self)
        self.cal_mag = CalibrateMagnetometer(self)
        self.cal_gyr_bias = CalibrateGyroscopeBias(self)
        self.cal_gyr_bias = CalibrateGyroscopeBias(self)
        self.cal_gyr_gain = CalibrateGyroscopeGain(self)
        self.cal_imex = CalibrateImportExport(self)
        
        
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self.current_tab_changed)
        self.tab_widget.addTab(self.cal_acc, "Accelerometer")
        self.tab_widget.addTab(self.cal_mag, "Magnetometer")
        self.tab_widget.addTab(self.cal_gyr_bias, "Gyroscope Bias")
        self.tab_widget.addTab(self.cal_gyr_gain, "Gyroscope Gain")
        self.tab_widget.addTab(self.cal_imex, "Im/Export")
        
        self.vlayout.addWidget(self.tab_widget)
        
        self.refresh_values()
        
    def closeEvent(self, event):
        self.parent.start()
        event.accept()
        
    def refresh_values(self):
        acc_gain = self.imu.get_calibration(self.TYPE_ACC_GAIN)
        acc_bias = self.imu.get_calibration(self.TYPE_ACC_BIAS)
        mag_gain = self.imu.get_calibration(self.TYPE_MAG_GAIN)
        mag_bias = self.imu.get_calibration(self.TYPE_MAG_BIAS)
        gyr_gain = self.imu.get_calibration(self.TYPE_GYR_GAIN)
        gyr_bias = self.imu.get_calibration(self.TYPE_GYR_BIAS)
        
        self.label_acc_gain_x.setText(str(acc_gain[0]) + '/' + str(acc_gain[3]))
        self.label_acc_gain_y.setText(str(acc_gain[1]) + '/' + str(acc_gain[4]))
        self.label_acc_gain_z.setText(str(acc_gain[2]) + '/' + str(acc_gain[5]))
        self.label_acc_bias_x.setText(str(acc_bias[0]))
        self.label_acc_bias_y.setText(str(acc_bias[1]))
        self.label_acc_bias_z.setText(str(acc_bias[2]))
        self.label_mag_gain_x.setText(str(mag_gain[0]) + '/' + str(mag_gain[3]))
        self.label_mag_gain_y.setText(str(mag_gain[1]) + '/' + str(mag_gain[4]))
        self.label_mag_gain_z.setText(str(mag_gain[2]) + '/' + str(mag_gain[5]))
        self.label_mag_bias_x.setText(str(mag_bias[0]))
        self.label_mag_bias_y.setText(str(mag_bias[1]))
        self.label_mag_bias_z.setText(str(mag_bias[2]))
        self.label_gyr_gain_x.setText(str(gyr_gain[0]) + '/' + str(gyr_gain[3]))
        self.label_gyr_gain_y.setText(str(gyr_gain[1]) + '/' + str(gyr_gain[4]))
        self.label_gyr_gain_z.setText(str(gyr_gain[2]) + '/' + str(gyr_gain[5]))
        self.label_gyr_bias_low_x.setText(str(gyr_bias[0]))
        self.label_gyr_bias_low_y.setText(str(gyr_bias[1]))
        self.label_gyr_bias_low_z.setText(str(gyr_bias[2]))
        self.label_gyr_bias_low_t.setText(str(gyr_bias[3]))
        self.label_gyr_bias_high_x.setText(str(gyr_bias[4]))
        self.label_gyr_bias_high_y.setText(str(gyr_bias[5]))
        self.label_gyr_bias_high_z.setText(str(gyr_bias[6]))
        self.label_gyr_bias_high_t.setText(str(gyr_bias[7]))
    
    def current_tab_changed(self, index):
        if index == 0:
            self.cal_acc.start()
            self.cal_mag.stop()
            self.cal_gyr_bias.stop()
            self.cal_gyr_gain.stop()
        elif index == 1:
            self.cal_acc.stop()
            self.cal_mag.start()
            self.cal_gyr_bias.stop()
            self.cal_gyr_gain.stop()
        elif index == 2:
            self.cal_acc.stop()
            self.cal_mag.stop()
            self.cal_gyr_bias.start()
            self.cal_gyr_gain.stop()
        elif index == 3:
            self.cal_acc.stop()
            self.cal_mag.stop()
            self.cal_gyr_bias.stop()
            self.cal_gyr_gain.start()
