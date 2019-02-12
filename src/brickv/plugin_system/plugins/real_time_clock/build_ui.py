#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("python3 ../../../../pyuic5-fixed.py -o ui_real_time_clock.py ui/real_time_clock.ui")
system("python3 ../../../../pyuic5-fixed.py -o ui_calibration.py ui/calibration.ui")
