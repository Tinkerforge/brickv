#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("python3 ../../../../pyuic5-fixed.py -o ui_analog_out_v3.py ui/analog_out_v3.ui")
