# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_importexport_export.py: RED import/export export tab implementation

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

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QWidget, QListWidgetItem
from brickv.plugin_system.plugins.red.ui_red_tab_importexport_export import Ui_REDTabImportExportExport
from brickv.plugin_system.plugins.red.api import *
from brickv.async_call import async_call

class REDTabImportExportExport(QWidget, Ui_REDTabImportExportExport):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session             = None # Set from REDTabImportExport
        self.script_manager      = None # Set from REDTabImportExport
        self.image_version       = None # Set from REDTabImportExport
        self.first_tab_on_focus  = True
        self.refresh_in_progress = False

        self.list_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_refresh_programs.clicked.connect(self.refresh_program_list)

        self.update_ui_state()

    def tab_on_focus(self):
        if self.first_tab_on_focus:
            self.first_tab_on_focus = False

            QTimer.singleShot(1, self.refresh_program_list)

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def update_ui_state(self):
        if self.refresh_in_progress:
            self.progress_refresh_programs.setVisible(True)
            self.button_refresh_programs.setText('Refreshing...')
            self.button_refresh_programs.setEnabled(False)
            self.button_export.setEnabled(False)
        else:
            self.progress_refresh_programs.setVisible(False)
            self.button_refresh_programs.setText('Refresh')
            self.button_refresh_programs.setEnabled(True)

            self.button_export.setEnabled(len(self.list_programs.selectedItems()) > 0)

    def refresh_program_list(self):
        def refresh_async():
            return get_simple_programs(self.session)

        def cb_success(programs):
            sorted_programs = {}

            for program in programs:
                first_upload = program.cast_custom_option_value('first_upload', int, 0)

                if first_upload in sorted_programs:
                    sorted_programs[first_upload][program.identifier] = program
                else:
                    sorted_programs[first_upload] = {program.identifier: program}

            for first_upload in sorted(sorted_programs.keys()):
                for identifier in sorted(sorted_programs[first_upload].keys()):
                    program = sorted_programs[first_upload][identifier]

                    item = QListWidgetItem(program.cast_custom_option_value('name', unicode, '<unknown>'))
                    item.setData(Qt.UserRole, identifier)

                    self.list_programs.addItem(item)

            self.refresh_in_progress = False
            self.update_ui_state()

        def cb_error():
            pass # FIXME: report error

        self.refresh_in_progress = True
        self.update_ui_state()
        self.list_programs.clear()

        async_call(refresh_async, None, cb_success, cb_error, log_exception=True)
