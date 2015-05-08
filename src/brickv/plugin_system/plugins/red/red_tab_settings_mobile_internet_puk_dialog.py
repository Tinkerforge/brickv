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

from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_mobile_internet_puk_dialog import Ui_REDTabSettingsMobileInternetPUKDialog
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call
from brickv.utils import get_main_window

EVENT_GUI_APPLY_CLICKED = 1
EVENT_GUI_APPLY_RETURNED = 2

MESSAGEBOX_TITLE = 'Settings | Mobile Internet'
MESSAGE_ERROR_PUK_EMPTY = 'PUK empty'
MESSAGE_ERROR_PIN_EMPTY = 'PIN empty'
MESSAGE_ERROR_PUK_OK = 'PUK operation successful'
MESSAGE_ERROR_PUK_FAILED = 'PUK operation failed'
MESSAGE_ERROR_NO_DEVICE = 'No mobile internet device found'

class REDTabSettingsMobileInternetPUKDialog(QtGui.QDialog, Ui_REDTabSettingsMobileInternetPUKDialog):
    def __init__(self, parent, session, script_manager):
        QtGui.QDialog.__init__(self, parent)

        self.setupUi(self)

        self.session = session
        self.script_manager = script_manager

        regex = QtCore.QRegExp("\\d+")
        validator = QtGui.QRegExpValidator(regex)
        self.ledit_mi_puk_puk.setValidator(validator)
        self.ledit_mi_puk_pin.setValidator(validator)

        self.pbutton_mi_puk_apply.clicked.connect(self.pbutton_mi_puk_apply_clicked)
        self.pbutton_mi_puk_cancel.clicked.connect(self.pbutton_mi_puk_cancel_clicked)

    def pbutton_mi_puk_apply_clicked(self):
        if not self.validate_fields():
            return

        self.update_gui(EVENT_GUI_APPLY_CLICKED)
        self.script_manager.execute_script('settings_mobile_internet',
                                           self.cb_settings_mobile_internet_puk,
                                           ['PUK',
                                            self.ledit_mi_puk_puk.text(),
                                            self.ledit_mi_puk_pin.text()])

    def pbutton_mi_puk_cancel_clicked(self):
        self.accept()

    def validate_fields(self):
        if not self.ledit_mi_puk_puk.text():
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_PUK_EMPTY)
            return False

        if not self.ledit_mi_puk_pin.text():
            QtGui.QMessageBox.critical(get_main_window(),
                                       MESSAGEBOX_TITLE,
                                       MESSAGE_ERROR_PIN_EMPTY)
            return False
        
        return True

    def update_gui(self, event):
        if event == EVENT_GUI_APPLY_CLICKED:
            self.pbutton_mi_puk_apply.setText('Applying...')
            self.ledit_mi_puk_puk.setEnabled(False)
            self.ledit_mi_puk_pin.setEnabled(False)
            self.pbutton_mi_puk_apply.setEnabled(False)
            self.pbutton_mi_puk_cancel.setEnabled(False)

        elif event == EVENT_GUI_APPLY_RETURNED:
            self.pbutton_mi_puk_apply.setText('Apply')
            self.ledit_mi_puk_puk.setEnabled(True)
            self.ledit_mi_puk_pin.setEnabled(True)
            self.pbutton_mi_puk_apply.setEnabled(True)
            self.pbutton_mi_puk_cancel.setEnabled(True)

    def cb_settings_mobile_internet_puk(self, result):
        print result
        self.update_gui(EVENT_GUI_APPLY_RETURNED)

        if result.exit_code == 2:
            QtGui.QMessageBox.critical(get_main_window(),
                                          MESSAGEBOX_TITLE,
                                          MESSAGE_ERROR_NO_DEVICE)
            return

        if not report_script_result(result, MESSAGEBOX_TITLE, MESSAGE_ERROR_PUK_FAILED):
            return

        QtGui.QMessageBox.information(get_main_window(),
                                      MESSAGEBOX_TITLE,
                                      MESSAGE_ERROR_PUK_OK)
        self.accept()
