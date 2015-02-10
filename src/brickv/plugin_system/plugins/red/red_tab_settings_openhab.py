# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_openhab.py: RED settings openHAB tab implementation

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

from PyQt4 import QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_openhab import Ui_REDTabSettingsOpenHAB
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.utils import get_main_window
import json

class REDTabSettingsOpenHAB(QtGui.QWidget, Ui_REDTabSettingsOpenHAB):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

    def tab_on_focus(self):
        self.label_unsupported.hide()
        self.label_disabled.hide()

        if self.image_version.number < (1, 6):
            self.label_unsupported.show()
        elif not self.service_state.openhab:
            self.label_disabled.show()

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass
