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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_puk_dialog import Ui_REDTabSettingsMobileInternetPUKDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.async_call import async_call
from brickv.utils import get_main_window
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_provider
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_country

class REDTabSettingsMobileInternetPUKDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetPUKDialog):
    def __init__(self, parent, session):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session

        regex = QtCore.QRegExp("\\d+")
        validator = QtGui.QRegExpValidator(regex)
        self.ledit_mi_puk_puk.setValidator(validator)
        self.ledit_mi_puk_pin.setValidator(validator)

        self.pbutton_mi_puk_apply.clicked.connect(self.pbutton_mi_puk_apply_clicked)
        self.pbutton_mi_puk_cancel.clicked.connect(self.pbutton_mi_puk_cancel_clicked)

    def pbutton_mi_puk_apply_clicked(self):
        self.accept()

    def pbutton_mi_puk_cancel_clicked(self):
        self.reject()
