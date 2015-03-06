#!/usr/bin/env python

import os

# main window
os.system("pyuic4 -o ui_mainwindow.py ui/brickv.ui")
os.system("pyuic4 -o ui_flashing.py ui/flashing.ui")
os.system("pyuic4 -o ui_advanced.py ui/advanced.ui")

