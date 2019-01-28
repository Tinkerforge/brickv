#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_sound_pressure_level.py ui/sound_pressure_level.ui")
