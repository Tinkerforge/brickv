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
from brickv.plugin_system.plugins.red.red_tab_settings_mobile_internet_provider_preset_dialog import REDTabSettingsMobileInternetProviderPresetDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import TextFile
from brickv.plugin_system.plugins.red import config_parser
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.plugin_system.plugins.red.serviceprovider_data import dict_provider, dict_country
from brickv.async_call import async_call
from brickv.utils import get_main_window

EVENT_GUI_INIT_OK = 1
EVENT_GUI_INIT_UNSUPPORTED = 2
EVENT_GUI_NO_DEVICE = 3
EVENT_GUI_REFRESH_CLICKED = 4
EVENT_GUI_REFRESH_RETURNED = 5
EVENT_GUI_CONNECT_CLICKED = 6
EVENT_GUI_CONNECT_RETURNED = 7

MESSAGEBOX_TITLE = 'Settings | Mobile Internet'
MESSAGE_ERROR_DETECT_DEVICE = 'Error detecting mobile internet device'
MESSAGE_ERROR_VALIDATION_APN_EMPTY = 'APN empty'
MESSAGE_ERROR_VALIDATION_APN_NON_ASCII = 'APN contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_USERNAME_EMPTY = 'Username empty'
MESSAGE_ERROR_VALIDATION_USERNAME_NON_ASCII = 'Username contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_PASSWORD_EMPTY = 'Password empty'
MESSAGE_ERROR_VALIDATION_PASSWORD_NON_ASCII = 'Password contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_NUMBER_EMPTY = 'Number empty'
MESSAGE_ERROR_VALIDATION_NUMBER_NON_ASCII = 'Number contains non ASCII characters'
MESSAGE_ERROR_REFERSH = 'Error occured while refreshing'
MESSAGE_ERROR_REFERSH_DECODE = 'Error occured while decoding refresh data'

INTERVAL_REFRESH_STATUS = 3000 # In miliseconds

class REDTabSettingsMobileInternet(QtGui.QWidget, Ui_REDTabSettingsMobileInternet):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.sarea_mi.hide()

        regex = QtCore.QRegExp("\\d+")
        validator = QtGui.QRegExpValidator(regex)
        self.ledit_mi_sim_pin.setValidator(validator)

        self.status_refresh_timer = Qt.QTimer(self)

        self.pbutton_mi_provider_presets.clicked.connect(self.pbutton_mi_provider_presets_clicked)
        self.pbutton_mi_refresh.clicked.connect(self.pbutton_mi_refresh_clicked)
        self.pbutton_mi_connect.clicked.connect(self.pbutton_mi_connect_clicked)
        self.status_refresh_timer.timeout.connect(self.status_refresh_timer_timeout)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        # Check image version
        if self.image_version.number < (1, 7):
            self.update_gui(EVENT_GUI_INIT_UNSUPPORTED)
            return

        self.update_gui(EVENT_GUI_INIT_OK)

        # Start status refresh timer
        self.status_refresh_timer.start(INTERVAL_REFRESH_STATUS)

        # Do initial refresh
        self.pbutton_mi_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False
        self.status_refresh_timer.stop()

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

    def pbutton_mi_refresh_clicked(self):
        self.update_gui(EVENT_GUI_REFRESH_CLICKED)

        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_refresh,
                                           ['REFRESH'])

    def pbutton_mi_connect_clicked(self):
        result, message = self.validate_configuration_fields()

        if not result:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       message)
            return
        
        self.update_gui(EVENT_GUI_CONNECT_CLICKED)
        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_connect,
                                           ['CONNECT'])

    def status_refresh_timer_timeout(self):
        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_get_status,
                                           ['GET_STATUS'])
        self.status_refresh_timer.stop()

    def cb_settings_mobile_internet_get_status(self, result):
        self.status_refresh_timer.start(INTERVAL_REFRESH_STATUS)
        # Update status GUI elements

    def cb_settings_mobile_internet_connect(self, result):
        self.update_gui(EVENT_GUI_CONNECT_RETURNED)

    def cb_settings_mobile_internet_refresh(self, result):
        self.update_gui(EVENT_GUI_REFRESH_RETURNED)

        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_REFERSH):
            return

        try:
            dict_configuration = json.loads(result.stdout)
        except:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_REFERSH_DECODE)
            return

        if dict_configuration['apn']:
            self.ledit_mi_apn.setText(dict_configuration['apn'])
        else:
            self.ledit_mi_apn.setText('')

        if dict_configuration['username']:
            self.ledit_mi_username.setText(dict_configuration['username'])
        else:
            self.ledit_mi_username.setText('')
        
        if dict_configuration['password']:
            self.ledit_mi_password.setText(dict_configuration['password'])
        else:
            self.ledit_mi_password.setText('')
        
        if dict_configuration['phone']:
            self.ledit_mi_number.setText(dict_configuration['phone'])
        else:
            self.ledit_mi_number.setText('')

        if dict_configuration['sim_card_pin']:
            self.ledit_mi_sim_pin.setText(dict_configuration['sim_card_pin'])
        else:
            self.ledit_mi_sim_pin.setText('')

    def check_ascii(self, text):
        try:
            text.encode('ascii')
            return True
        except:
            return False

    def validate_configuration_fields(self):
        apn = self.ledit_mi_apn.text()
        username = self.ledit_mi_username.text()
        password = self.ledit_mi_password.text()
        number = self.ledit_mi_number.text()

        if not apn:
            return False, MESSAGE_ERROR_VALIDATION_APN_EMPTY
        if not self.check_ascii(apn):
            return False, MESSAGE_ERROR_VALIDATION_APN_NON_ASCII

        if not username:
            return False, MESSAGE_ERROR_VALIDATION_USERNAME_EMPTY
        if not self.check_ascii(username):
            return False, MESSAGE_ERROR_VALIDATION_USERNAME_NON_ASCII

        if not password:
            return False, MESSAGE_ERROR_VALIDATION_PASSWORD_EMPTY
        if not self.check_ascii(password):
            return False, MESSAGE_ERROR_VALIDATION_PASSWORD_NON_ASCII

        if not number:
            return False, MESSAGE_ERROR_VALIDATION_NUMBER_EMPTY
        if not self.check_ascii(number):
            return False, MESSAGE_ERROR_VALIDATION_NUMBER_NON_ASCII

        return True, None

    def update_gui(self, event):
        if event == EVENT_GUI_INIT_OK:
            self.label_mi_unsupported.hide()
            self.label_mi_working_wait.hide()
            self.pbar_mi_working_wait.hide()
            self.sarea_mi.show()

        elif event == EVENT_GUI_INIT_UNSUPPORTED:
            self.label_mi_unsupported.show()
            self.label_mi_working_wait.hide()
            self.pbar_mi_working_wait.hide()
            self.sarea_mi.hide()

        elif event == EVENT_GUI_REFRESH_CLICKED or event == EVENT_GUI_CONNECT_CLICKED:
            self.label_mi_working_wait.show()
            self.pbar_mi_working_wait.show()

            if event == EVENT_GUI_REFRESH_CLICKED:
                self.pbutton_mi_refresh.setText('Refreshing...')
            if event == EVENT_GUI_CONNECT_CLICKED:
                self.pbutton_mi_connect.setText('Connecting...')

            self.sarea_mi.setEnabled(False)

        elif event == EVENT_GUI_REFRESH_RETURNED or event == EVENT_GUI_CONNECT_RETURNED:
            self.label_mi_working_wait.hide()
            self.pbar_mi_working_wait.hide()
            self.pbutton_mi_refresh.setText('Refresh')
            self.pbutton_mi_connect.setText('Connect')
            self.sarea_mi.setEnabled(True)
