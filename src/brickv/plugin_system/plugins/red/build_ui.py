#!/usr/bin/env python

import os

os.system("pyuic4 -o ui_red.py ui/red.ui")
os.system("pyuic4 -o ui_red_tab_overview.py ui/red_tab_overview.ui")
os.system("pyuic4 -o ui_red_tab_settings.py ui/red_tab_settings.ui")
os.system("pyuic4 -o ui_red_tab_program.py ui/red_tab_program.ui")
os.system("pyuic4 -o ui_red_tab_console.py ui/red_tab_console.ui")
os.system("pyuic4 -o ui_red_tab_versions.py ui/red_tab_versions.ui")
