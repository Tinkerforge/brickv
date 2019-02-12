#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("python3 ../../pyuic5-fixed.py -o ui_setup_dialog.py ui/setup_dialog.ui")
system("python3 ../../pyuic5-fixed.py -o ui_device_dialog.py ui/device_dialog.ui")
