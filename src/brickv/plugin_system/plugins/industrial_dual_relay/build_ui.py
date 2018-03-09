#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_industrial_dual_relay.py ui/industrial_dual_relay.ui")
