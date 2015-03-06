#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_solid_state_relay.py ui/solid_state_relay.ui")
