#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_real_time_clock.py ui/real_time_clock.ui")
system("pyuic4 -o ui_calibration.py ui/calibration.ui")
