#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_industrial_digital_in_4.py ui/industrial_digital_in_4.ui")
