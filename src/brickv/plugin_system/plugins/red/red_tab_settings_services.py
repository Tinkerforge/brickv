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
from brickv.utils import get_main_window
import json

class REDTabSettingsServices(QtGui.QWidget, Ui_REDTabSettingsServices):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        self.apply_dict = {'gpu':          None,
                           'desktopenv':   None,
                           'webserver':    None,
                           'splashscreen': None}

        self.pbutton_services_save.clicked.connect(self.slot_pbutton_services_save_clicked)
        self.pbutton_services_refresh.clicked.connect(self.slot_pbutton_services_refresh_clicked)

        self.chkbox_gpu.stateChanged.connect(self.service_config_changed)
        self.chkbox_desktopenv.stateChanged.connect(self.service_config_changed)
        self.chkbox_webserver.stateChanged.connect(self.service_config_changed)
        self.chkbox_splashscreen.stateChanged.connect(self.service_config_changed)

        self.all_checkbox(False)

    def all_checkbox(self, state):
        if state:
            self.chkbox_gpu.setEnabled(True)
            self.chkbox_desktopenv.setEnabled(True)
            self.chkbox_webserver.setEnabled(True)
            self.chkbox_splashscreen.setEnabled(True)
            self.chkbox_gpu.setChecked(False)
            self.chkbox_desktopenv.setChecked(False)
            self.chkbox_webserver.setChecked(False)
            self.chkbox_splashscreen.setChecked(False)
        else:
            self.chkbox_gpu.setChecked(False)
            self.chkbox_desktopenv.setChecked(False)
            self.chkbox_webserver.setChecked(False)
            self.chkbox_splashscreen.setChecked(False)
            self.chkbox_gpu.setEnabled(False)
            self.chkbox_desktopenv.setEnabled(False)
            self.chkbox_webserver.setEnabled(False)
            self.chkbox_splashscreen.setEnabled(False)

    def tab_on_focus(self):
        self.is_tab_on_focus = True
        self.all_checkbox(False)
        self.slot_pbutton_services_refresh_clicked()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    def cb_settings_services_check(self, result):
        if not self.is_tab_on_focus:
            return

        self.pbutton_services_refresh.setEnabled(True)
        self.pbutton_services_refresh.setText('Refresh')

        if result and result.stdout and not result.stderr and result.exit_code == 0:
            services_check_result = json.loads(result.stdout)
            if services_check_result:
                if services_check_result['gpu'] is None or \
                   services_check_result['desktopenv'] is None or \
                   services_check_result['webserver'] is None or \
                   services_check_result['splashscreen'] is None:
                    self.all_checkbox(False)
                    QtGui.QMessageBox.critical(get_main_window(),
                                               'Settings | Services',
                                               'Error getting current services status.',
                                               QtGui.QMessageBox.Ok)

                    return
                else:
                    self.all_checkbox(True)
                    if services_check_result['gpu']:
                        self.chkbox_gpu.setChecked(True)
                    else:
                        self.chkbox_gpu.setChecked(False)

                    if services_check_result['desktopenv']:
                        self.chkbox_desktopenv.setChecked(True)
                    else:
                        self.chkbox_desktopenv.setChecked(False)

                    if services_check_result['webserver']:
                        self.chkbox_webserver.setChecked(True)
                    else:
                        self.chkbox_webserver.setChecked(False)

                    if services_check_result['splashscreen']:
                        self.chkbox_splashscreen.setChecked(True)
                    else:
                        self.chkbox_splashscreen.setChecked(False)
                    self.pbutton_services_save.setEnabled(False)
        else:
            err_msg = 'Error getting current services status.\n\n'+unicode(result.stderr)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Services',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

    def cb_settings_services_apply(self, result):
        print result

        self.chkbox_gpu.setEnabled(True)
        self.chkbox_desktopenv.setEnabled(True)
        self.chkbox_webserver.setEnabled(True)
        self.chkbox_splashscreen.setEnabled(True)

        self.pbutton_services_save.setText('Save')
        self.pbutton_services_save.setEnabled(True)
        self.pbutton_services_refresh.setEnabled(True)

        if result and result.stdout and not result.stderr and result.exit_code == 0:
            def cb_restart_reboot_shutdown(result):
                if result is not None:
                    if not result.stderr and result.exit_code == 0:
                        pass
                    else:
                        err_msg = 'Error rebooting RED Brick.\n\n'+unicode(result.stderr)
    
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | Services',
                                                   err_msg,
                                                   QtGui.QMessageBox.Ok)

            self.script_manager.execute_script('restart_reboot_shutdown',
                                               cb_restart_reboot_shutdown, ['1'])
        else:
            err_msg = 'Error saving services status.\n\n'+unicode(result.stderr)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | Services',
                                       err_msg,
                                       QtGui.QMessageBox.Ok)

    def service_config_changed(self, state):
        self.pbutton_services_save.setEnabled(True)

    def slot_pbutton_services_save_clicked(self):
        print 'slot_pbutton_services_save_clicked'
        if self.chkbox_gpu.isChecked():
            self.apply_dict['gpu'] = True
        else:
            self.apply_dict['gpu'] = False

        if self.chkbox_desktopenv.isChecked():
            self.apply_dict['desktopenv'] = True
        else:
            self.apply_dict['desktopenv'] = False

        if self.chkbox_webserver.isChecked():
            self.apply_dict['webserver'] = True
        else:
            self.apply_dict['webserver'] = False

        if self.chkbox_splashscreen.isChecked():
            self.apply_dict['splashscreen'] = True
        else:
            self.apply_dict['splashscreen'] = False

        self.chkbox_gpu.setEnabled(False)
        self.chkbox_desktopenv.setEnabled(False)
        self.chkbox_webserver.setEnabled(False)
        self.chkbox_splashscreen.setEnabled(False)

        self.pbutton_services_save.setText('Saving...')
        self.pbutton_services_save.setEnabled(False)
        self.pbutton_services_refresh.setEnabled(False)

        self.script_manager.execute_script('settings_services',
                                           self.cb_settings_services_apply,
                                           ['APPLY', unicode(json.dumps(self.apply_dict))])

    def slot_pbutton_services_refresh_clicked(self):
        self.all_checkbox(False)
        self.pbutton_services_save.setEnabled(False)
        self.pbutton_services_refresh.setText('Refreshing...')
        self.pbutton_services_refresh.setEnabled(False)
        self.script_manager.execute_script('settings_services',
                                           self.cb_settings_services_check,
                                           ['CHECK'])
