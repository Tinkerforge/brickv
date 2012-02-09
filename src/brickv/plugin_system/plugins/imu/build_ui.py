#!/usr/bin/env python

import os

os.system("pyuic4 -o ui_imu.py ui/imu.ui")
os.system("pyuic4 -o ui_calibrate.py ui/calibrate.ui")
os.system("pyuic4 -o ui_calibrate_accelerometer.py ui/calibrate_accelerometer.ui")
os.system("pyuic4 -o ui_calibrate_magnetometer.py ui/calibrate_magnetometer.ui")
os.system("pyuic4 -o ui_calibrate_gyroscope_gain.py ui/calibrate_gyroscope_gain.ui")
os.system("pyuic4 -o ui_calibrate_gyroscope_bias.py ui/calibrate_gyroscope_bias.ui")
os.system("pyuic4 -o ui_calibrate_temperature.py ui/calibrate_temperature.ui")
os.system("pyuic4 -o ui_calibrate_import_export.py ui/calibrate_import_export.ui")
