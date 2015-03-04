# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings_server_monitoring_add_host_dialog.py: RED settings server monitoring add host dialog implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_settings_server_monitoring_add_host_dialog \
     import Ui_REDTabSettingsServerMonitoringAddHostDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.utils import get_main_window

class REDTabSettingsServerMonitoringAddHostDialog(QtGui.QDialog, Ui_REDTabSettingsServerMonitoringAddHostDialog):
    def __init__(self, parent):
        QtGui.QDialog.__init__(self, parent)
        self.setupUi(self)

        self.chkbox_sm_add_host_authentication.stateChanged.connect(self.slot_chkbox_sm_add_host_authentication_state_changed)
        self.pbutton_sm_add_host_add.clicked.connect(self.slot_pbutton_sm_add_host_add_clicked)
        self.pbutton_sm_add_host_cancel.clicked.connect(self.slot_pbutton_sm_add_host_cancel_clicked)

        if self.chkbox_sm_add_host_authentication.checkState() == QtCore.Qt.Checked:
            self.label_sm_add_host_secret.show()
            self.ledit_sm_add_host_secret.show()
        else:
            self.label_sm_add_host_secret.hide()
            self.ledit_sm_add_host_secret.hide()

    def slot_pbutton_sm_add_host_cancel_clicked(self):
        self.reject()

    def slot_pbutton_sm_add_host_add_clicked(self):
        #if check fails then self.reject() otherwise self.accept()

        try:
            self.ledit_sm_add_host_host.text().encode('ascii')
            return True
        except:
            return False

    def slot_chkbox_sm_add_host_authentication_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            self.label_sm_add_host_secret.show()
            self.ledit_sm_add_host_secret.show()
        else:
            self.label_sm_add_host_secret.hide()
            self.ledit_sm_add_host_secret.hide()
