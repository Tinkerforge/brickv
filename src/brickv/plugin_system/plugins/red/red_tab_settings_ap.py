# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_ap.py: RED settings access point tab implementation

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
General Public License for more details.

You should have received a copy of the GNU General Public
License along with this program; if not, write to the
Free Software Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
"""

import json
from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_ap import Ui_REDTabSettingsAP
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

# Constants

class REDTabSettingsAP(QtGui.QWidget, Ui_REDTabSettingsAP):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings

        self.is_tab_on_focus = False

    def tab_on_focus(self):
        self.is_tab_on_focus = True

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass
