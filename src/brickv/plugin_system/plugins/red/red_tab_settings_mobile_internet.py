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
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_provider, dict_country
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

        self.label_working_wait.hide()
        self.pbar_working_wait.hide()

        self.pbutton_mi_provider_presets.clicked.connect(self.pbutton_mi_provider_presets_clicked)
        self.pbutton_mi_enter_puk.clicked.connect(self.pbutton_mi_enter_puk_clicked)
        self.pbutton_mi_refresh.clicked.connect(self.pbutton_mi_refresh_clicked)
        self.pbutton_mi_connect.clicked.connect(self.pbutton_mi_connect_clicked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def pbutton_mi_provider_presets_clicked(self):
        provider_preset_dialog = REDTabSettingsMobileInternetProviderPresetDialog(self,
                                                                                  self.session,
                                                                                  dict_provider,
                                                                                  dict_country)
        if provider_preset_dialog.exec_() == QtGui.QDialog.Accepted:
            if provider_preset_dialog.label_mi_preview_apn.text() and \
               provider_preset_dialog.label_mi_preview_apn.text() != '-':
                    self.ledit_mi_apn.setText(provider_preset_dialog.label_mi_preview_apn.text())
            else:
                self.ledit_mi_apn.setText('')

            if provider_preset_dialog.label_mi_preview_username.text() and \
               provider_preset_dialog.label_mi_preview_username.text() != '-':
                    self.ledit_mi_username.setText(provider_preset_dialog.label_mi_preview_username.text())
            else:
                self.ledit_mi_username.setText('')

            if provider_preset_dialog.label_mi_preview_password.text() and \
               provider_preset_dialog.label_mi_preview_password.text() != '-':
                    self.ledit_mi_password.setText(provider_preset_dialog.label_mi_preview_password.text())
            else:
                self.ledit_mi_password.setText('')

            if provider_preset_dialog.label_mi_preview_number.text() and \
               provider_preset_dialog.label_mi_preview_number.text() != '-':
                    self.ledit_mi_number.setText(provider_preset_dialog.label_mi_preview_number.text())
            else:
                self.ledit_mi_number.setText('')

        provider_preset_dialog.done(0)

    def pbutton_mi_enter_puk_clicked(self):
        puk_dialog = REDTabSettingsMobileInternetPUKDialog(self, self.session)

        if puk_dialog.exec_() == QtGui.QDialog.Accepted:
            puk = puk_dialog.ledit_mi_puk_puk.text()
            pin = puk_dialog.ledit_mi_puk_pin.text()

            if not puk or not pin:
                return

            # Call the script here

        puk_dialog.done(0)

    def pbutton_mi_refresh_clicked(self):
        pass

    def pbutton_mi_connect_clicked(self):
        pass

    def show_working_wait(self, show):
        if show:
            self.label_working_wait.show()
            self.pbar_working_wait.show()
        else:
            self.label_working_wait.hide()
            self.pbar_working_wait.hide()
