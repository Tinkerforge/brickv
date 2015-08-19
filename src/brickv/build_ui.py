#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_mainwindow.py ui/mainwindow.ui")
system("pyuic4 -o ui_flashing.py ui/flashing.ui")
system("pyuic4 -o ui_advanced.py ui/advanced.ui")
system("pyuic4 -o ui_logger_setup.py ui/logger_setup.ui")
system("pyuic4 -o ui_device_dialog.py ui/device_dialog.ui")
