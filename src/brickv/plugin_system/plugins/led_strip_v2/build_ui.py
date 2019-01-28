#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_led_strip_v2.py ui/led_strip_v2.ui")
