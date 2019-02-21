#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_segment_display_4x7_v2.py ui/segment_display_4x7_v2.ui")
