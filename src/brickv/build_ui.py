#!/usr/bin/env python

import os

# main window
os.system("pyuic4 -o ui_mainwindow.py ui/brickv.ui")
os.system("pyuic4 -o ui_updates.py ui/updates.ui")
os.system("pyuic4 -o ui_flashing.py ui/flashing.ui")
os.system("pyuic4 -o ui_advanced.py ui/advanced.ui")

# Servo Brick
os.system("pyuic4 -o plugin_system/plugins/servo/ui_servo.py plugin_system/plugins/servo/ui/servo.ui")
