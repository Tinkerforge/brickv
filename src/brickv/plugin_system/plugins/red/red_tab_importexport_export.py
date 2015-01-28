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

import os
import time

from PyQt4.QtCore import Qt, QTimer, QDateTime
from PyQt4.QtGui import QWidget, QListWidgetItem, QMessageBox

from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path, get_save_file_name
from brickv.plugin_system.plugins.red.ui_red_tab_importexport_export import Ui_REDTabImportExportExport
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import ChunkedDownloaderBase, ExpandingProgressDialog
from brickv.plugin_system.plugins.red.script_manager import report_script_result

class ChunkedDownloader(ChunkedDownloaderBase):
    def __init__(self, widget):
        ChunkedDownloaderBase.__init__(self, widget.session)

        self.widget = widget

    def report_error(self, message, *args):
        string_args = []

        for arg in args:
            string_args.append(Qt.escape(unicode(arg)))

        if len(string_args) > 0:
            message = unicode(message).format(*tuple(string_args))

        QMessageBox.critical(get_main_window(), 'Export Error', message)

    def set_progress_maximum(self, maximum):
        progress = self.widget.progress

        if progress != None:
            progress.setRange(0, maximum)

    def set_progress_value(self, value, message):
        progress = self.widget.progress

        if progress != None:
            progress.setValue(value)
            progress.set_progress_text(message)

    def done(self):
        self.widget.chunked_downloader = None
        self.widget.progress.close()
        self.widget.progress = None

        QMessageBox.information(get_main_window(), 'Export Success',
                                'Selected programs successfully exported.')


class REDTabImportExportExport(QWidget, Ui_REDTabImportExportExport):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session             = None # Set from REDTabImportExport
        self.script_manager      = None # Set from REDTabImportExport
        self.image_version       = None # Set from REDTabImportExport
        self.first_tab_on_focus  = True
        self.refresh_in_progress = False
        self.last_directory      = get_home_path()
        self.progress            = None
        self.chunked_downloader  = None

        self.list_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_refresh_programs.clicked.connect(self.refresh_program_list)
        self.button_export.clicked.connect(self.export)

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

                    item.setSelected(True)

            self.refresh_in_progress = False
            self.update_ui_state()

        def cb_error():
            pass # FIXME: report error

        self.refresh_in_progress = True
        self.update_ui_state()
        self.list_programs.clear()

        async_call(refresh_async, None, cb_success, cb_error, log_exception=True)

    def export(self):
        timestamp   = QDateTime.fromTime_t(int(time.time())).toString('yyyyMMdd-HHmmss')
        target_path = os.path.join(self.last_directory, 'red-brick-export-{0}.tfrba'.format(timestamp))
        target_path = get_save_file_name(get_main_window(), 'Save Archive', target_path)

        if len(target_path) == 0:
            return

        self.last_directory = os.path.split(target_path)[0]
        script_instance_ref = [None]

        def progress_canceled():
            script_instance = script_instance_ref[0]

            if script_instance != None:
                self.script_manager.abort_script(script_instance)

            chunked_downloader = self.chunked_downloader

            if chunked_downloader != None:
                chunked_downloader.canceled = True

        self.progress = ExpandingProgressDialog(self)
        self.progress.set_progress_text_visible(False)
        self.progress.setModal(True)
        self.progress.setWindowTitle('Exporting Archive')
        self.progress.setLabelText('Archiving selected programs')
        self.progress.setRange(0, 0)
        self.progress.canceled.connect(progress_canceled)
        self.progress.show()

        selected_identifiers = []

        for selected_item in self.list_programs.selectedItems():
            selected_identifiers.append(selected_item.data(Qt.UserRole))

        def cb_export(result):
            script_instance = script_instance_ref[0]

            if script_instance != None:
                aborted = script_instance.abort
            else:
                aborted = False

            script_instance_ref[0] = None

            if aborted:
                return

            if not report_script_result(result, 'Export Error', 'Could not archive selected programs'):
                return

            source_path             = os.path.join(result.stdout.strip(), 'archive.tfrba')
            self.chunked_downloader = ChunkedDownloader(self)

            if not self.chunked_downloader.prepare(source_path):
                return

            self.progress.setLabelText('Downloading archive')
            self.progress.set_progress_text_visible(True)
            self.chunked_downloader.start(target_path)

        script_instance_ref[0] = self.script_manager.execute_script('export', cb_export, selected_identifiers)
