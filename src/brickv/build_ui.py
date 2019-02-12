#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("python3 ../pyuic5-fixed.py -o ui_mainwindow.py ui/mainwindow.ui")
system("python3 ../pyuic5-fixed.py -o ui_flashing.py ui/flashing.ui")
system("python3 ../pyuic5-fixed.py -o ui_advanced.py ui/advanced.ui")
