# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_importexport_import.py: RED import/export import tab implementation

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
import posixpath
import tarfile
import contextlib

from PyQt4.QtCore import Qt, QTimer
from PyQt4.QtGui import QWidget, QTreeWidgetItem, QMessageBox

from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path, get_open_file_name
from brickv.plugin_system.plugins.red.ui_red_tab_importexport_import import Ui_REDTabImportExportImport
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import Constants, ChunkedUploaderBase, ExpandingProgressDialog
from brickv.plugin_system.plugins.red.script_manager import report_script_result

class ChunkedUploader(ChunkedUploaderBase):
    def __init__(self, widget, done_callback):
        ChunkedUploaderBase.__init__(self, widget.session)

        self.widget        = widget
        self.done_callback = done_callback

    def report_error(self, message, *args):
        string_args = []

        for arg in args:
            string_args.append(Qt.escape(unicode(arg)))

        if len(string_args) > 0:
            message = unicode(message).format(*tuple(string_args))

        self.widget.progress.close()
        QMessageBox.critical(get_main_window(), 'Import Error', message)

    def set_progress_maximum(self, maximum):
        if self.widget.progress.isVisible():
            self.widget.progress.setRange(0, maximum)

    def set_progress_value(self, value, message):
        if self.widget.progress.isVisible():
            self.widget.progress.setValue(value)
            self.widget.progress.set_progress_text(message)

    def done(self):
        self.widget.chunked_uploader = None

        self.done_callback()


class REDTabImportExportImport(QWidget, Ui_REDTabImportExportImport):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session             = None # Set from REDTabImportExport
        self.script_manager      = None # Set from REDTabImportExport
        self.image_version       = None # Set from REDTabImportExport
        self.refresh_in_progress = False
        self.progress            = None
        self.chunked_uploader    = None

        self.button_browse_archive.clicked.connect(self.browse_archive)
        self.edit_archive.textChanged.connect(self.update_ui_state)
        self.tree_programs.setColumnWidth(0, 150)
        self.tree_programs.setColumnWidth(1, 150)
        self.tree_programs.setColumnWidth(2, 150)
        self.tree_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_refresh_programs.clicked.connect(self.refresh_program_list)
        self.button_import.clicked.connect(self.import_archive)

        self.update_ui_state()

    def tab_on_focus(self):
        QTimer.singleShot(1, self.refresh_program_list)

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass

    def update_ui_state(self):
        if self.refresh_in_progress:
            self.edit_archive.setEnabled(False)
            self.button_browse_archive.setEnabled(False)
            self.progress_refresh_programs.setVisible(True)
            self.button_refresh_programs.setText('Refreshing...')
            self.button_refresh_programs.setEnabled(False)
            self.button_import.setEnabled(False)
        else:
            self.edit_archive.setEnabled(True)
            self.button_browse_archive.setEnabled(True)
            self.progress_refresh_programs.setVisible(False)
            self.button_refresh_programs.setText('Refresh')
            self.button_refresh_programs.setEnabled(len(self.edit_archive.text()) > 0)
            self.button_import.setEnabled(len(self.tree_programs.selectedItems()) > 0)

    def browse_archive(self):
        if len(self.edit_archive.text()) > 0:
            last_directory = os.path.dirname(os.path.realpath(self.edit_archive.text()))
        else:
            last_directory = get_home_path()

        filename = get_open_file_name(get_main_window(), 'Open Archive', last_directory, '*.tfrba')

        if len(filename) > 0:
            self.edit_archive.setText(filename)
            self.refresh_program_list()

    def refresh_program_list(self):
        filename = self.edit_archive.text()

        if len(filename) == 0:
            return

        def refresh_async():
            try:
                a = tarfile.open(filename, 'r:gz')
            except Exception as e:
                return [], u'Could not open archive:\n\n{0}'.format(e)

            with contextlib.closing(a):
                try:
                    v = a.extractfile('tfrba-version')
                except Exception as e:
                    return [], u'Could not extract tfrba-version:\n\n{0}'.format(e)

                version = v.read()
                v.close()

                if version != '1':
                    return [], u'Unknown tfrba-version {0}'.format(version)

                programs = {}

                for member in a.getnames():
                    if member.startswith('programs/') and member.endswith('/program.conf'):
                        try:
                            c = a.extractfile(member)
                        except Exception as e:
                            return [], u'Could not extract {0}:\n\n{1}'.format(member, e)

                        conf = c.readlines()
                        c.close()

                        name         = '<unknown>'
                        identifier   = member.split('/')[1]
                        language     = '<unknown>'
                        first_upload = 0

                        for line in conf:
                            if line.startswith('custom.name ='):
                                try:
                                    name = line[len('custom.name ='):].strip().decode('string_escape').decode('utf-8')
                                except:
                                    pass
                            elif line.startswith('custom.language ='):
                                try:
                                    language = Constants.get_language_display_name(line[len('custom.language ='):].strip().decode('string_escape'))
                                except:
                                    pass
                            elif line.startswith('custom.first_upload ='):
                                try:
                                    first_upload = int(line[len('custom.first_upload ='):].strip())
                                except:
                                    pass

                        programs[identifier] = [name, identifier, language, 'New', first_upload]

                try:
                    existing_programs = get_simple_programs(self.session)
                except Exception as e:
                    return [], u'Could not get existing program list:\n\n{0}'.format(e)

                for existing_program in existing_programs:
                    identifier = existing_program.identifier

                    if identifier in programs:
                        programs[identifier][3] = 'Existing'

                return programs.values(), None

        def cb_success(result):
            programs, message = result

            if message != None:
                QMessageBox.critical(get_main_window(), 'Import Error', message)
            else:
                sorted_programs = {}

                for program in programs:
                    first_upload = program[4]

                    if first_upload in sorted_programs:
                        sorted_programs[first_upload][program[1]] = program
                    else:
                        sorted_programs[first_upload] = {program[1]: program}

                for first_upload in sorted(sorted_programs.keys()):
                    for identifier in sorted(sorted_programs[first_upload].keys()):
                        program = sorted_programs[first_upload][identifier]
                        item    = QTreeWidgetItem(program[0:4])

                        self.tree_programs.addTopLevelItem(item)

                        item.setSelected(True)

            self.refresh_in_progress = False
            self.update_ui_state()
            self.tree_programs.setFocus()

        def cb_error(error):
            pass # FIXME: report error

        self.refresh_in_progress = True
        self.update_ui_state()
        self.tree_programs.invisibleRootItem().takeChildren()

        async_call(refresh_async, None, cb_success, cb_error, report_exception=True)

    def import_archive(self):
        source_path = self.edit_archive.text()

        if len(source_path) == 0:
            return

        script_instance_ref = [None]

        def progress_canceled():
            chunked_uploader = self.chunked_uploader

            if chunked_uploader != None:
                chunked_uploader.canceled = True

            script_instance = script_instance_ref[0]

            if script_instance != None:
                self.script_manager.abort_script(script_instance)

        self.progress = ExpandingProgressDialog(self)
        self.progress.set_progress_text_visible(False)
        self.progress.setModal(True)
        self.progress.setWindowTitle('Import Archive')
        self.progress.setLabelText('Step 1 of 4: Creating import directory')
        self.progress.setRange(0, 0)
        self.progress.setAutoClose(False)
        self.progress.canceled.connect(progress_canceled)
        self.progress.show()

        selected_identifiers = []

        for selected_item in self.tree_programs.selectedItems():
            selected_identifiers.append(selected_item.text(1))

        import_directory_ref = [None]

        def extract_archive():
            def cb_import_extract(result):
                script_instance = script_instance_ref[0]

                if script_instance != None:
                    aborted = script_instance.abort
                else:
                    aborted = False

                script_instance_ref[0] = None

                if aborted:
                    return

                if not report_script_result(result, 'Import Error', 'Could not extract archive',
                                            before_message_box=self.progress.close):
                    return

                def cb_restart_reboot_shutdown(result):
                    self.progress.close()

                    report_script_result(result, 'Import Error', 'Could not reboot RED Brick to finish program import')

                # step 4/4: reboot
                self.progress.setLabelText('Step 4 of 4: Rebooting RED Brick')
                self.progress.setRange(0, 0)

                self.script_manager.execute_script('restart_reboot_shutdown',
                                                   cb_restart_reboot_shutdown, ['1'])

                def close_progress():
                    # use a closure to capture self and ansure that it's safe
                    # to call this even if the tab was official destroyed already
                    self.progress.close()

                QTimer.singleShot(1500, close_progress)

            # step 3/4: extract uploaded archive
            self.progress.setLabelText('Step 3 of 4: Extracting archive')
            self.progress.setRange(0, 0)

            script_instance_ref[0] = self.script_manager.execute_script('import_extract', cb_import_extract,
                                                                        [import_directory_ref[0]] + selected_identifiers)

        def cb_import_directory(result):
            script_instance = script_instance_ref[0]

            if script_instance != None:
                aborted = script_instance.abort
            else:
                aborted = False

            script_instance_ref[0] = None

            if aborted:
                return

            if not report_script_result(result, 'Import Error', 'Could not create import directory',
                                        before_message_box=self.progress.close):
                return

            # step 2/4: upload archive to temporary import directory
            import_directory_ref[0] = result.stdout.strip()
            target_path             = posixpath.join(import_directory_ref[0], 'archive.tfrba')
            self.chunked_uploader   = ChunkedUploader(self, extract_archive)

            if not self.chunked_uploader.prepare(source_path):
                return

            try:
                target_file = REDFile(self.session).open(target_path, REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_EXCLUSIVE, 0o644, 1000, 1000) # FIXME: async_call
            except (Error, REDError) as e:
                QMessageBox.information(get_main_window(), 'Import Error',
                                        'Could not open target file {0}: {1}'.format(target_path, e))
                return

            self.progress.setLabelText('Step 2 of 4: Uploading archive')
            self.progress.set_progress_text_visible(True)
            self.chunked_uploader.start(target_path, target_file)

        # step 1/4: create temporary import directory
        script_instance_ref[0] = self.script_manager.execute_script('import_directory', cb_import_directory, execute_as_user=True)
