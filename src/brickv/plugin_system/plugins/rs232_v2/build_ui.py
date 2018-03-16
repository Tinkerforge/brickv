#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_rs232_v2.py ui/rs232_v2.ui")
