#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("python3 ../../../../pyuic5-fixed.py -o ui_imu.py ui/imu.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate.py ui/calibrate.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_accelerometer.py ui/calibrate_accelerometer.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_magnetometer.py ui/calibrate_magnetometer.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_gyroscope_gain.py ui/calibrate_gyroscope_gain.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_gyroscope_bias.py ui/calibrate_gyroscope_bias.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_temperature.py ui/calibrate_temperature.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibrate_import_export.py ui/calibrate_import_export.ui")
