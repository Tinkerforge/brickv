# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_mobile_internet.py: RED settings mobile internet tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet import Ui_REDTabSettingsMobileInternet
from brickv.plugin_system.plugins.red.red_tab_settings_mobile_internet_puk_dialog import REDTabSettingsMobileInternetPUKDialog
from brickv.plugin_system.plugins.red.red_tab_settings_mobile_internet_provider_preset_dialog import REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

class REDTabSettingsMobileInternet(QtGui.QWidget, Ui_REDTabSettingsMobileInternet):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.pbutton_mi_enter_puk.clicked.connect(self.pbutton_mi_enter_puk_clicked)
        self.pbutton_mi_provider_presets.clicked.connect(self.pbutton_mi_provider_presets_clicked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def pbutton_mi_enter_puk_clicked(self):
        puk_dialog = REDTabSettingsMobileInternetPUKDialog(self, self.session)
        puk_dialog.setModal(True)
        puk_dialog.show()

    def pbutton_mi_provider_presets_clicked(self):
        provider_preset_dialog = REDTabSettingsMobileInternetProviderPresetDialog(self, self.session)
        provider_preset_dialog.setModal(True)
        provider_preset_dialog.show()
