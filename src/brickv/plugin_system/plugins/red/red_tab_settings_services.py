# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_services.py: RED settings services tab implementation

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
import sys
import time
import math
from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_services import Ui_REDTabSettingsServices
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

class REDTabSettingsServices(QtGui.QWidget, Ui_REDTabSettingsServices):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from RED Tab Settings
        self.script_manager = None # Set from RED Tab Settings

        self.is_tab_on_focus = False

        self.apply_dict = {'gpu'   :None,
                           'de'    :None,
                           'web'   :None,
                           'splash':None}

        self.pbutton_services_save.clicked.connect(self.slot_pbutton_services_save_clicked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True
        self.script_manager.execute_script('settings_services',
                                           self.cb_settings_services,
                                           ['CHECK'])

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def cb_settings_services(self, result):
        pass

    def check_services(self):
        pass
    
    def slot_pbutton_services_save_clicked(self):
        print 'slot_pbutton_services_save_clicked'
        if self.chkbox_gpu.isChecked():
            self.apply_dict['gpu'] = True
        else:
            self.apply_dict['gpu'] = False

        if self.chkbox_de.isChecked():
            self.apply_dict['de'] = True
        else:
            self.apply_dict['de'] = False

        if self.chkbox_web.isChecked():
            self.apply_dict['web'] = True
        else:
            self.apply_dict['web'] = False

        if self.chkbox_splash.isChecked():
            self.apply_dict['splash'] = True
        else:
            self.apply_dict['splash'] = False

        self.script_manager.execute_script('settings_services',
                                           self.cb_settings_services,
                                           ['APPLY', unicode(json.dumps(self.apply_dict))])
