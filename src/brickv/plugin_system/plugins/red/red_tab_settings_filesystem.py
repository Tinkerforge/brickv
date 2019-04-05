# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_settings_filesystem.py: RED settings file system tab implementation

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
import math

from PyQt5.QtWidgets import QWidget, QMessageBox

from brickv.plugin_system.plugins.red.ui_red_tab_settings_filesystem import Ui_REDTabSettingsFileSystem
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import report_script_result
from brickv.utils import get_main_window
from brickv.config import get_use_fusion_gui_style

class REDTabSettingsFileSystem(QWidget, Ui_REDTabSettingsFileSystem):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # Set from REDTabSettings
        self.script_manager = None # Set from REDTabSettings
        self.image_version  = None # Set from REDTabSettings
        self.service_state  = None # Set from REDTabSettings

        self.is_tab_on_focus = False

        # For macOS progress bar text fix
        self.label_fs_expand_info.hide()
        self.line.hide()
        self.label_pbar_fs_capacity_utilization.hide()

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

        if not report_script_result(result, 'Settings | File System',
                                    'Error getting partition information'):
            self.label_fs_expand_info.hide()
            self.line.hide()
            self.label_pbar_fs_capacity_utilization.hide()
            self.pbar_fs_capacity_utilization.setMinimum(0)
            self.pbar_fs_capacity_utilization.setMaximum(100)
            self.pbar_fs_capacity_utilization.setValue(0)
            self.pbar_fs_capacity_utilization.setFormat('')
            self.pbar_fs_capacity_utilization.setEnabled(False)
            self.pbutton_fs_expand.setEnabled(False)
            return

        try:
            size_dict = json.loads(result.stdout)
            p1_start = float(size_dict['p1_start'])
            p1_size = float(size_dict['p1_size'])
            card_size = float(size_dict['card_size'])
            ext3_size = float(size_dict['ext3_size'])
        except:
            p1_start = 0
            p1_size = 100
            card_size = 100
            ext3_size = 100

        avialable_size = card_size - p1_start
        used_size = min(p1_size, ext3_size)

        percentage_utilization_v = min(int(math.ceil((used_size / avialable_size) * 100.0)), 100)

        # due to common file system overhead 100% will normally never be
        # reached just fake 100% in this case to avoid user confusion
        if percentage_utilization_v >= 95:
            percentage_utilization_v = 100

        percentage_utilization = str(percentage_utilization_v)

        self.pbar_fs_capacity_utilization.setEnabled(True)

        self.pbar_fs_capacity_utilization.setMinimum(0)
        self.pbar_fs_capacity_utilization.setMaximum(100)

        self.pbar_fs_capacity_utilization.setValue(percentage_utilization_v)

        if percentage_utilization_v == 100:
            self.pbutton_fs_expand.setEnabled(False)
            self.label_fs_expand_info.hide()
            self.line.hide()
        else:
            self.pbutton_fs_expand.setEnabled(True)
            self.label_fs_expand_info.show()
            self.line.show()

        pbar_fs_capacity_utilization_fmt = "Using {0}% of total capacity".format(percentage_utilization)

        if sys.platform == 'darwin' and not get_use_fusion_gui_style():
            self.label_pbar_fs_capacity_utilization.show()
            self.label_pbar_fs_capacity_utilization.setText(pbar_fs_capacity_utilization_fmt)
        else:
            self.pbar_fs_capacity_utilization.setFormat(pbar_fs_capacity_utilization_fmt)

    # The slots
    def slot_fs_expand_clicked(self):
        def cb_settings_fs_expand(result):
            def cb_restart_reboot_shutdown(result):
                report_script_result(result, 'Settings | File System',
                                     'Error rebooting RED Brick')

            get_main_window().setEnabled(True)

            if not report_script_result(result, 'Settings | File System',
                                        'Error expanding file system'):
                return

            QMessageBox.information(get_main_window(),
                                          'Settings | Services',
                                          'File system expansion will be complete after reboot, rebooting RED Brick now.')

            self.script_manager.execute_script('restart_reboot_shutdown_systemd',
                                               cb_restart_reboot_shutdown, ['1'])

        get_main_window().setEnabled(False)
        self.script_manager.execute_script('settings_fs_expand',
                                           cb_settings_fs_expand)
