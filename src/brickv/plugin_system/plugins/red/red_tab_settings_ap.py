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

        self.ap_mode = False
        self.label_ap_disabled.hide()

    def tab_on_focus(self):
        self.is_tab_on_focus = True
        
        def cb_settings_network_ap_check(result):
            if result and not result.stderr and result.exit_code == 0:
                ap_mode_check = json.loads(result.stdout)
                if ap_mode_check['ap_image_version'] is None or \
                   ap_mode_check['ap_interface'] is None or \
                   ap_mode_check['ap_enabled'] is None:
                        self.sarea_ap.setEnabled(False)
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Access Point',
                                                   'Error checking access point mode.',
                                                   QtGui.QMessageBox.Ok)
                elif ap_mode_check['ap_image_version'] and \
                     ap_mode_check['ap_interface'] and \
                     ap_mode_check['ap_enabled']:
                        self.ap_mode_enabled()
                else:
                    self.ap_mode_disabled()
            else:
                err_msg = 'Error checking access point mode\n\n'+unicode(result.stderr)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | Access Point',
                                           err_msg,
                                           QtGui.QMessageBox.Ok)

        self.script_manager.execute_script('settings_network_ap_check',
                                           cb_settings_network_ap_check)

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def ap_mode_enabled(self):
        self.ap_mode = True
        self.label_ap_disabled.hide()
        self.sarea_ap.setEnabled(True)

    def ap_mode_disabled(self):
        self.ap_mode = False
        self.label_ap_disabled.show()
        self.sarea_ap.setEnabled(False)
