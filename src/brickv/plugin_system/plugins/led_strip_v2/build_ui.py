#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_led_strip_v2.py ui/led_strip_v2.ui")
