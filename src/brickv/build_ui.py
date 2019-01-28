#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_mainwindow.py ui/mainwindow.ui")
system("pyuic5 -o ui_flashing.py ui/flashing.ui")
system("pyuic5 -o ui_advanced.py ui/advanced.ui")
