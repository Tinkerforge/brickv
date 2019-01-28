#!/usr/bin/env python3

import os

def system(command):
    if os.system(command) != 0:
        exit(1)

system("pyuic5 -o ui_master.py ui/master.ui")
system("pyuic5 -o ui_chibi.py ui/chibi.ui")
system("pyuic5 -o ui_rs485.py ui/rs485.ui")
system("pyuic5 -o ui_wifi.py ui/wifi.ui")
system("pyuic5 -o ui_wifi2.py ui/wifi2.ui")
system("pyuic5 -o ui_ethernet.py ui/ethernet.ui")
system("pyuic5 -o ui_wifi_status.py ui/wifi_status.ui")
system("pyuic5 -o ui_wifi2_status.py ui/wifi2_status.ui")
system("pyuic5 -o ui_extension_type.py ui/extension_type.ui")
