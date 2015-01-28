# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4 import QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_services import Ui_REDTabSettingsServices
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.utils import get_main_window
import json

class REDTabSettingsServices(QtGui.QWidget, Ui_REDTabSettingsServices):
    def __init__(self):
        QtGui.QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.chkbox_gpu.stateChanged.connect(self.service_config_changed)
        self.chkbox_desktopenv.stateChanged.connect(self.service_config_changed)
        self.chkbox_webserver.stateChanged.connect(self.service_config_changed)
        self.chkbox_splashscreen.stateChanged.connect(self.service_config_changed)
        self.chkbox_ap.stateChanged.connect(self.service_config_changed)
        self.pbutton_services_save.clicked.connect(self.slot_pbutton_services_save_clicked)

    def tab_on_focus(self):
        self.chkbox_gpu.setEnabled(True)
        self.chkbox_desktopenv.setEnabled(True)
        self.chkbox_webserver.setEnabled(True)
        self.chkbox_splashscreen.setEnabled(True)
        self.chkbox_ap.setEnabled(True)
        self.pbutton_services_save.setText('Save')
        self.pbutton_services_save.setEnabled(False)

        self.chkbox_gpu.setChecked(self.service_state.gpu)
        self.chkbox_desktopenv.setChecked(self.service_state.desktopenv)
        self.chkbox_webserver.setChecked(self.service_state.webserver)
        self.chkbox_splashscreen.setChecked(self.service_state.splashscreen)
        self.chkbox_ap.setChecked(self.service_state.ap)

        if self.image_version.number < (1, 4):
            self.chkbox_gpu.setText('Enable GPU (Image Version >= 1.4 required)')
            self.chkbox_gpu.setEnabled(False)

            self.chkbox_desktopenv.setText('Start Desktop Environment (Image Version >= 1.4 required)')
            self.chkbox_desktopenv.setEnabled(False)

            self.chkbox_webserver.setText('Start Web Server (Image Version >= 1.4 required)')
            self.chkbox_webserver.setEnabled(False)

            self.chkbox_splashscreen.setText('Show Splash Screen (Image Version >= 1.4 required)')
            self.chkbox_splashscreen.setEnabled(False)

            self.chkbox_ap.setText('Access Point Mode (Image Version >= 1.4 required)')
            self.chkbox_ap.setEnabled(False)

            self.pbutton_services_save.setEnabled(False)

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def cb_settings_services_apply(self, result):
        def done():
            self.chkbox_gpu.setEnabled(True)
            self.chkbox_desktopenv.setEnabled(True)
            self.chkbox_webserver.setEnabled(True)
            self.chkbox_splashscreen.setEnabled(True)
            self.chkbox_ap.setEnabled(True)

            self.pbutton_services_save.setText('Save')
            self.pbutton_services_save.setEnabled(True)

        if not report_script_result(result, 'Settings | Services', 'Error saving services status'):
            done()
            return

        def cb_restart_reboot_shutdown(result):
            if not report_script_result(result, 'Settings | Services', 'Error rebooting RED Brick'):
                done()
                return

        self.script_manager.execute_script('restart_reboot_shutdown',
                                           cb_restart_reboot_shutdown, ['1'])

    def service_config_changed(self, state):
        self.pbutton_services_save.setEnabled(True)

    def slot_pbutton_services_save_clicked(self):
        state = {}

        state['gpu']          = self.chkbox_gpu.isChecked()
        state['desktopenv']   = self.chkbox_desktopenv.isChecked()
        state['webserver']    = self.chkbox_webserver.isChecked()
        state['splashscreen'] = self.chkbox_splashscreen.isChecked()
        state['ap']           = self.chkbox_ap.isChecked()

        self.chkbox_gpu.setEnabled(False)
        self.chkbox_desktopenv.setEnabled(False)
        self.chkbox_webserver.setEnabled(False)
        self.chkbox_splashscreen.setEnabled(False)
        self.chkbox_ap.setEnabled(False)

        self.pbutton_services_save.setText('Saving...')
        self.pbutton_services_save.setEnabled(False)

        self.script_manager.execute_script('settings_services',
                                           self.cb_settings_services_apply,
                                           ['APPLY', json.dumps(state)])
