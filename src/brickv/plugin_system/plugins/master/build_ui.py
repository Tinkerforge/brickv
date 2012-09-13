#!/usr/bin/env python

import os

os.system("pyuic4 -o ui_master.py ui/master.ui")
os.system("pyuic4 -o ui_chibi.py ui/chibi.ui")
os.system("pyuic4 -o ui_rs485.py ui/rs485.ui")
os.system("pyuic4 -o ui_wifi.py ui/wifi.ui")
os.system("pyuic4 -o ui_wifi_status.py ui/wifi_status.ui")
os.system("pyuic4 -o ui_extension_type.py ui/extension_type.ui")
