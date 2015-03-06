#!/usr/bin/env python

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic4 -o ui_master.py ui/master.ui")
system("pyuic4 -o ui_chibi.py ui/chibi.ui")
system("pyuic4 -o ui_rs485.py ui/rs485.ui")
system("pyuic4 -o ui_wifi.py ui/wifi.ui")
system("pyuic4 -o ui_ethernet.py ui/ethernet.ui")
system("pyuic4 -o ui_wifi_status.py ui/wifi_status.ui")
system("pyuic4 -o ui_extension_type.py ui/extension_type.ui")
