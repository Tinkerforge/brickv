# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_file_system.py: RED settings file system tab implementation

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
import sys
import time
import math
from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_settings_file_system import Ui_REDTabSettingsFileSystem
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser
from brickv.async_call import async_call
from brickv.utils import get_main_window

# Constants

class REDTabSettingsFileSystem(QtGui.QWidget, Ui_REDTabSettingsFileSystem):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)
        
        self.session        = None # Set from RED Tab Settings
        self.script_manager = None # Set from RED Tab Settings

        self.is_tab_on_focus = False

        # For OSX progress bar text fix
        self.label_fs_expand_info.hide()
        self.label_pbar_fs_capacity_utilization.hide()

        self.label_fs_spacer.setText('')

        # Signals/slots
        self.pbutton_fs_expand.clicked.connect(self.slot_fs_expand_clicked)

    def tab_on_focus(self):
        self.is_tab_on_focus = True
        self.script_manager.execute_script('settings_fs_expand_check',
                                           self.cb_settings_fs_expand_check,
                                           ['/dev/mmcblk0'])

    def tab_off_focus(self):
        self.is_tab_on_focus = False

    def tab_destroy(self):
        pass

    # The callbacks
    def cb_settings_fs_expand_check(self, result):
        if not self.is_tab_on_focus:
            return

        if result and result.stdout and not result.stderr and result.exit_code == 0:
            try:
                size_dict = json.loads(result.stdout)
                p1_start = float(size_dict['p1_start'])
                p1_size = float(size_dict['p1_size'])
                card_size = float(size_dict['card_size'])
            except:
                p1_start = 0
                p1_size = 100
                card_size = 100

            percentage_utilization_v = min(int(math.ceil((p1_size / (card_size - p1_start)) * 100.0)), 100)
            percentage_utilization = unicode(percentage_utilization_v)

            self.pbar_fs_capacity_utilization.setEnabled(True)

            self.pbar_fs_capacity_utilization.setMinimum(0)
            self.pbar_fs_capacity_utilization.setMaximum(100)

            self.pbar_fs_capacity_utilization.setValue(percentage_utilization_v)

            if percentage_utilization_v >= 95:
                self.pbutton_fs_expand.setEnabled(False)
                self.label_fs_expand_info.hide()
                self.label_fs_spacer.show()
            else:
                self.pbutton_fs_expand.setEnabled(True)
                self.label_fs_expand_info.show()
                self.label_fs_spacer.hide()

            pbar_fs_capacity_utilization_fmt = "Using {0}% of total capacity".format(percentage_utilization)

            if sys.platform == 'darwin':
                self.label_pbar_fs_capacity_utilization.show()
                self.label_pbar_fs_capacity_utilization.setText(pbar_fs_capacity_utilization_fmt)
            else:
                self.pbar_fs_capacity_utilization.setFormat(pbar_fs_capacity_utilization_fmt)
        else:
            self.label_fs_expand_info.hide()
            self.label_pbar_fs_capacity_utilization.hide()
            self.pbar_fs_capacity_utilization.setMinimum(0)
            self.pbar_fs_capacity_utilization.setMaximum(100)
            self.pbar_fs_capacity_utilization.setValue(0)
            self.pbar_fs_capacity_utilization.setFormat('')
            self.pbar_fs_capacity_utilization.setEnabled(False)

            err_msg = ''
            if result.stderr:
                err_msg = unicode(result.stderr)

            self.pbutton_fs_expand.setEnabled(False)
            QtGui.QMessageBox.critical(get_main_window(),
                                       'Settings | File System',
                                       'Error getting partition information.\n\n'+err_msg,
                                       QtGui.QMessageBox.Ok)

    # The slots
    def slot_fs_expand_clicked (self):
        def cb_settings_fs_expand(result):
            def cb_restart_reboot_shutdown(result):
                self.pbutton_fs_expand.setEnabled(False)
                if result is not None:
                    if not result.stderr and result.exit_code == 0:
                        pass
                    else:
                        err_msg = ''
                        if result.stderr:
                            err_msg = unicode(result.stderr)
    
                        QtGui.QMessageBox.critical(get_main_window(),
                                                   'Settings | File System',
                                                   'Error rebooting RED Brick.\n\n'+err_msg,
                                                   QtGui.QMessageBox.Ok)

            if result and result.stdout and not result.stderr and result.exit_code == 0:
                self.script_manager.execute_script('restart_reboot_shutdown',
                                                   cb_restart_reboot_shutdown,
                                                   [unicode(1)])
            else:
                self.pbutton_fs_expand.setEnabled(True)

                err_msg = ''
                if result.stderr:
                    err_msg = unicode(result.stderr)
                QtGui.QMessageBox.critical(get_main_window(),
                                           'Settings | File System',
                                           'Error expanding file system.\n\n'+err_msg,
                                           QtGui.QMessageBox.Ok)

        self.pbutton_fs_expand.setEnabled(False)
        self.script_manager.execute_script('settings_fs_expand',
                                           cb_settings_fs_expand)
