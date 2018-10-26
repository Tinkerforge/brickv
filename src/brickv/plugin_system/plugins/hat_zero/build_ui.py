#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_hat_zero.py ui/hat_zero.ui")
