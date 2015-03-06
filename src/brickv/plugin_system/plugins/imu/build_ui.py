#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_imu.py ui/imu.ui")
system("pyuic4 -o ui_calibrate.py ui/calibrate.ui")
system("pyuic4 -o ui_calibrate_accelerometer.py ui/calibrate_accelerometer.ui")
system("pyuic4 -o ui_calibrate_magnetometer.py ui/calibrate_magnetometer.ui")
system("pyuic4 -o ui_calibrate_gyroscope_gain.py ui/calibrate_gyroscope_gain.ui")
system("pyuic4 -o ui_calibrate_gyroscope_bias.py ui/calibrate_gyroscope_bias.ui")
system("pyuic4 -o ui_calibrate_temperature.py ui/calibrate_temperature.ui")
system("pyuic4 -o ui_calibrate_import_export.py ui/calibrate_import_export.ui")
