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
EVENT_GUI_REFRESH_CLICKED = 3
EVENT_GUI_REFRESH_RETURNED = 4
EVENT_GUI_CONNECT_CLICKED = 5
EVENT_GUI_CONNECT_RETURNED = 6

MESSAGEBOX_TITLE = 'Settings | Mobile Internet'
MESSAGE_ERROR_DETECT_DEVICE = 'Error detecting mobile internet device'
MESSAGE_ERROR_VALIDATION_APN_EMPTY = 'APN empty'
MESSAGE_ERROR_VALIDATION_APN_NON_ASCII = 'APN contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_USERNAME_NON_ASCII = 'Username contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_PASSWORD_NON_ASCII = 'Password contains non ASCII characters'
MESSAGE_ERROR_VALIDATION_PIN_EMPTY = 'SIM card PIN empty'
MESSAGE_ERROR_VALIDATION_PIN_LENGTH = 'SIM card PIN not 4 digits'
MESSAGE_ERROR_REFERSH = 'Error occurred while refreshing'
MESSAGE_ERROR_REFERSH_DECODE = 'Error occurred while decoding refresh data'
MESSAGE_ERROR_STATUS_DECODE = 'Error occurred while decoding status data'
MESSAGE_ERROR_CONNECT = 'Error occurred while connecting'
MESSAGE_ERROR_CONNECT_TEST = 'Error occurred while connecting. Make sure the configuration is correct'
MESSAGE_ERROR_CONNECT_SERVICE_CREATION = 'Error occurred while connecting. systemd service creation failed'
MESSAGE_ERROR_CONNECT_SERVICE_EXECUTION = 'Error occurred while connecting. systemd service execution failed'
MESSAGE_INFORMATION_CONNECT_OK = 'Configuration saved and applied successfully'

INTERVAL_REFRESH_STATUS = 15000 # In milliseconds

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

        regex_sim_card_pin = QtCore.QRegExp('\\d+')
        validator_sim_card_pin = QtGui.QRegExpValidator(regex_sim_card_pin)
        self.ledit_mi_sim_card_pin.setValidator(validator_sim_card_pin)
        
        regex_dial = QtCore.QRegExp('[\\d*#]+')
        validator_dial = QtGui.QRegExpValidator(regex_dial)
        self.ledit_mi_dial.setValidator(validator_dial)

        self.status_refresh_timer = Qt.QTimer(self)

        self.pbutton_mi_provider_presets.clicked.connect(self.pbutton_mi_provider_presets_clicked)
        self.pbutton_mi_refresh.clicked.connect(self.pbutton_mi_refresh_clicked)
        self.pbutton_mi_connect.clicked.connect(self.pbutton_mi_connect_clicked)
        self.status_refresh_timer.timeout.connect(self.status_refresh_timer_timeout)
        self.chkbox_mi_enable_pin.stateChanged.connect(self.chkbox_mi_enable_pin_state_changed)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        # Check image version
        if self.image_version.number < (1, 7):
            self.update_gui(EVENT_GUI_INIT_UNSUPPORTED)
            return

        # Initial GUI
        self.update_gui(EVENT_GUI_INIT_OK)

        # Start status refreshing
        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_get_status,
                                           ['GET_STATUS'])

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

            if provider_preset_dialog.label_mi_preview_dial.text() and \
               provider_preset_dialog.label_mi_preview_dial.text() != '-':
                    self.ledit_mi_dial.setText(provider_preset_dialog.label_mi_preview_dial.text())
            else:
                self.ledit_mi_dial.setText('*99#')

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
        
        usb_modem = self.cbox_mi_modem.itemData(self.cbox_mi_modem.currentIndex())
        
        if self.ledit_mi_dial.text():
            dial = self.ledit_mi_dial.text()
        else:
            dial = '*99#'

        apn = self.ledit_mi_apn.text()

        if self.ledit_mi_username.text():
            apn_user = self.ledit_mi_username.text()
        else:
            apn_user = 'none'

        if self.ledit_mi_password.text():
            apn_pass = self.ledit_mi_password.text()
        else:
            apn_pass = 'none'

        if self.chkbox_mi_enable_pin.isChecked():
            sim_pin = self.ledit_mi_sim_card_pin.text()
        else:
            sim_pin = ''

        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_connect,
                                           ['CONNECT',
                                            usb_modem,
                                            dial,
                                            apn,
                                            apn_user,
                                            apn_pass,
                                            sim_pin])

    def status_refresh_timer_timeout(self):
        self.status_refresh_timer.stop()
        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_get_status,
                                           ['GET_STATUS'])

    def chkbox_mi_enable_pin_state_changed(self):
        if self.chkbox_mi_enable_pin.isChecked():
            self.ledit_mi_sim_card_pin.setEnabled(True)
        else:
            self.ledit_mi_sim_card_pin.setEnabled(False)

    def cb_settings_mobile_internet_get_status(self, result):
        self.status_refresh_timer.stop()

        if not self.is_tab_on_focus:
            return

        if not result or result.exit_code != 0:
            self.status_refresh_timer.start(INTERVAL_REFRESH_STATUS)
            return

        try:
            dict_status = json.loads(result.stdout)
        except Exception as e:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_STATUS_DECODE + ':\n\n' +str(e))

            self.status_refresh_timer.start(INTERVAL_REFRESH_STATUS)
            return

        # Update status GUI elements
        if not dict_status['status']:
            self.label_mi_status_status.setText('-')
        else:
            self.label_mi_status_status.setText(dict_status['status'])
            
        if not dict_status['interface']:
            self.label_mi_status_interface.setText('-')
        else:
            self.label_mi_status_interface.setText(dict_status['interface'])
            
        if not dict_status['ip']:
            self.label_mi_status_ip.setText('-')
        else:
            self.label_mi_status_ip.setText(dict_status['ip'])
            
        if not dict_status['subnet_mask']:
            self.label_mi_status_subnet_mask.setText('-')
        else:
            self.label_mi_status_subnet_mask.setText(dict_status['subnet_mask'])
            
        if not dict_status['gateway']:
            self.label_mi_status_gateway.setText('-')
        else:
            self.label_mi_status_gateway.setText(dict_status['gateway'])
            
        if not dict_status['dns']:
            self.label_mi_status_dns.setText('-')
        else:
            self.label_mi_status_dns.setText(dict_status['dns'])

        self.status_refresh_timer.start(INTERVAL_REFRESH_STATUS)

    def cb_settings_mobile_internet_connect(self, result):
        self.update_gui(EVENT_GUI_CONNECT_RETURNED)

        if result.exit_code == 2:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CONNECT_TEST)
            return
        
        if result.exit_code == 3:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CONNECT_SERVICE_CREATION)
            return
    
        if result.exit_code == 4:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_CONNECT_SERVICE_EXECUTION)
            return

        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_CONNECT):
            return

        QtGui.QMessageBox.information(get_main_window(),
                                      MESSAGEBOX_TITLE,
                                      MESSAGE_INFORMATION_CONNECT_OK)

        self.pbutton_mi_refresh_clicked()

    def cb_settings_mobile_internet_refresh(self, result):
        self.update_gui(EVENT_GUI_REFRESH_RETURNED)

        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_REFERSH):
            return

        try:
            dict_configuration = json.loads(result.stdout)
        except Exception as e:
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_REFERSH_DECODE + ':\n\n' +str(e))
            return

        if not dict_configuration['modem_list']:
            self.cbox_mi_modem.clear()
        else:
            self.cbox_mi_modem.clear()

            for dict_modem in dict_configuration['modem_list']:
                self.cbox_mi_modem.addItem(dict_modem['name'])
                self.cbox_mi_modem.setItemData(self.cbox_mi_modem.count() - 1, dict_modem['vid_pid'])

        if dict_configuration['modem_configured']:
            for i in range(self.cbox_mi_modem.count()):
                if dict_configuration['modem_configured'] != self.cbox_mi_modem.itemData(i):
                    continue
                
                self.cbox_mi_modem.setCurrentIndex(i)
                break

        if not dict_configuration['dial']:
            self.ledit_mi_dial.setText('')
        else:
            self.ledit_mi_dial.setText(dict_configuration['dial'])

        if not dict_configuration['apn']:
            self.ledit_mi_apn.setText('')
        else:
            self.ledit_mi_apn.setText(dict_configuration['apn'])
        
        if not dict_configuration['username']:
            self.ledit_mi_username.setText('')
        else:
            self.ledit_mi_username.setText(dict_configuration['username'])
        
        if not dict_configuration['password']:
            self.ledit_mi_password.setText('')
        else:
            self.ledit_mi_password.setText(dict_configuration['password'])

        if not dict_configuration['sim_card_pin']:
            self.ledit_mi_sim_card_pin.setText('')
            self.chkbox_mi_enable_pin.setChecked(False)
            self.chkbox_mi_enable_pin_state_changed()
        else:
            self.chkbox_mi_enable_pin.setChecked(True)
            self.chkbox_mi_enable_pin_state_changed()
            self.ledit_mi_sim_card_pin.setText(dict_configuration['sim_card_pin'])

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

        if not apn:
            return False, MESSAGE_ERROR_VALIDATION_APN_EMPTY
        if not self.check_ascii(apn):
            return False, MESSAGE_ERROR_VALIDATION_APN_NON_ASCII

        if username and not self.check_ascii(username):
            return False, MESSAGE_ERROR_VALIDATION_USERNAME_NON_ASCII
    
        if password and not self.check_ascii(password):
            return False, MESSAGE_ERROR_VALIDATION_PASSWORD_NON_ASCII

        if self.chkbox_mi_enable_pin.isChecked():
            if not self.ledit_mi_sim_card_pin.text():
                return False, MESSAGE_ERROR_VALIDATION_PIN_EMPTY
            if len(self.ledit_mi_sim_card_pin.text()) != 4:
                return False, MESSAGE_ERROR_VALIDATION_PIN_LENGTH

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
