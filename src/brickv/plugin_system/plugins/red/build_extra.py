#!/usr/bin/env python3

import os
import sys

def system(command):
    if os.system(command) != 0:
        exit(1)

system(sys.executable + " build_scripts.py")

if sys.platform.startswith("linux"):
    system(sys.executable + " build_serviceproviders.py")
else:
    print("Skipping build_serviceproviders.py")
