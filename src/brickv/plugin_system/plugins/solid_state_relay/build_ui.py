#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_solid_state_relay.py ui/solid_state_relay.ui")
