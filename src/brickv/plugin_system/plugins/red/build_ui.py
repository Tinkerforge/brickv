#!/usr/bin/env python

import os

os.system("pyuic4 -o ui_red.py ui/red.ui")
os.system("pyuic4 -o ui_red_tab_overview.py ui/red_tab_overview.ui")
os.system("pyuic4 -o ui_red_tab_settings.py ui/red_tab_settings.ui")
os.system("pyuic4 -o ui_red_tab_program.py ui/red_tab_program.ui")
os.system("pyuic4 -o ui_red_tab_console.py ui/red_tab_console.ui")
os.system("pyuic4 -o ui_red_tab_versions.py ui/red_tab_versions.ui")
os.system("pyuic4 -o ui_red_tab_extension.py ui/red_tab_extension.ui")
os.system("pyuic4 -o ui_red_tab_extension_ethernet.py ui/red_tab_extension_ethernet.ui")
os.system("pyuic4 -o ui_new_program_general.py ui/new_program_general.ui")
os.system("pyuic4 -o ui_new_program_files.py ui/new_program_files.ui")
os.system("pyuic4 -o ui_new_program_java.py ui/new_program_java.ui")
os.system("pyuic4 -o ui_new_program_python.py ui/new_program_python.ui")
os.system("pyuic4 -o ui_new_program_arguments.py ui/new_program_arguments.ui")
os.system("pyuic4 -o ui_new_program_stdio.py ui/new_program_stdio.ui")
os.system("pyuic4 -o ui_new_program_schedule.py ui/new_program_schedule.ui")
os.system("python build_scripts.py")
