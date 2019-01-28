#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_industrial_quad_relay.py ui/industrial_quad_relay.ui")
