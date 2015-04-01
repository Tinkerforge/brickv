#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_industrial_analog_out.py ui/industrial_analog_out.ui")
