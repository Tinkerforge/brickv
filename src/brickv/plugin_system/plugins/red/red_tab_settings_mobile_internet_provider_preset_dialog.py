# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_mobile_internet_puk_dialog.py: RED settings mobile internet puk dialog implementation

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

from PyQt4 import QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_provider_preset_dialog import Ui_REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window

class REDTabSettingsMobileInternetProviderPresetDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetProviderPresetDialog):
    def __init__(self, parent, session, dict_provider, dict_country):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        self.cbox_mi_presets_country.clear()

        for key in dict_country:
            self.cbox_mi_presets_country.addItem(dict_country[key])
