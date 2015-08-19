#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_setup_dialog.py ui/setup_dialog.ui")
system("pyuic4 -o ui_device_dialog.py ui/device_dialog.ui")
