#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_rgb_led_matrix.py ui/rgb_led_matrix.ui")
