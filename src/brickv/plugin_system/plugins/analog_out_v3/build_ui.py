#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_analog_out_v3.py ui/analog_out_v3.ui")
