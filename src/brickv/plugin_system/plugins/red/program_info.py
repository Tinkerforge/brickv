# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

program_info.py: Program Info Widget

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

from PyQt4.QtCore import pyqtSignal
from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem, QDialog, QFileDialog
from brickv.plugin_system.plugins.red.program_wizard_edit import ProgramWizardEdit
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.program_page_general import ProgramPageGeneral
from brickv.plugin_system.plugins.red.program_page_java import ProgramPageJava
from brickv.plugin_system.plugins.red.program_page_python import ProgramPagePython
from brickv.plugin_system.plugins.red.program_page_ruby import ProgramPageRuby
from brickv.plugin_system.plugins.red.program_page_shell import ProgramPageShell
from brickv.plugin_system.plugins.red.program_page_arguments import ProgramPageArguments
from brickv.plugin_system.plugins.red.program_page_stdio import ProgramPageStdio
from brickv.plugin_system.plugins.red.program_page_schedule import ProgramPageSchedule
from brickv.plugin_system.plugins.red.ui_program_info import Ui_ProgramInfo
from brickv.async_call import async_call
import json

log_files_to_process = -1
log_files_download_dir = ""

class ProgramInfo(QWidget, Ui_ProgramInfo):
    name_changed = pyqtSignal()

    def __init__(self, session, program, script_manager, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session = session
        self.program = program
        self.script_manager = script_manager

        self.edit_general_wizard = None
        self.edit_arguments_wizard = None
        self.edit_stdio_wizard = None

        self.program_dir = unicode(self.program.root_directory)
        self.program_dir_walk_result = None
        self.tree_logs_model = QStandardItemModel(self)
        self.tree_logs_header_labels = ["File", "Time"]
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        self.tree_logs.setModel(self.tree_logs_model)

        self.tree_logs_model.itemChanged.connect(self.tree_logs_model_item_changed)
        self.button_refresh.clicked.connect(self.refresh_info)
        self.button_download_log.clicked.connect(self.download_selected_log)
        self.button_delete_log.clicked.connect(self.delete_selected_log)
        self.button_upload_files.clicked.connect(self.upload_files)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)
        self.button_edit_general.clicked.connect(self.show_edit_general_wizard)
        self.button_edit_language.clicked.connect(self.show_edit_language_wizard)
        self.button_edit_arguments.clicked.connect(self.show_edit_arguments_wizard)
        self.button_edit_stdio.clicked.connect(self.show_edit_stdio_wizard)
        self.button_edit_schedule.clicked.connect(self.show_edit_schedule_wizard)

        self.update_ui_state()

    def tree_logs_model_item_changed(self, idx):
        print idx

    def refresh_info(self):
        def refresh_async():
            self.program.update()

        def cb_success():
            self.button_refresh.setText("Refresh")
            self.button_refresh.setEnabled(True)
            self.update_ui_state()

        def cb_error():
            self.button_refresh.setText("Error")

        self.button_refresh.setText("Refreshing...")
        self.button_refresh.setEnabled(False)

        async_call(refresh_async, None, cb_success, cb_error)

    def update_ui_state(self):
        print "UUIS"

        has_files_selection = len(self.tree_files.selectedItems()) > 0

        self.button_download_files.setEnabled(has_files_selection)
        self.button_rename_file.setEnabled(len(self.tree_files.selectedItems()) == 1)
        self.button_delete_files.setEnabled(has_files_selection)

        # general
        name = self.program.cast_custom_option_value(Constants.FIELD_NAME, unicode, '<unknown>')
        api_language = self.program.cast_custom_option_value(Constants.FIELD_LANGUAGE, unicode, '<unknown>')
        description = self.program.cast_custom_option_value('description', unicode, '')

        try:
            language = Constants.get_language(api_language)
            language_display_name = Constants.language_display_names[language]
        except:
            language_display_name = '<unknown>'

        self.label_name.setText(name)
        self.label_identifier.setText(unicode(self.program.identifier))
        self.label_language.setText(language_display_name)
        self.label_description.setText(description)

        # logs
        def cb_program_get_os_walk(result):
            if result.stderr == "":
                self.program_dir_walk_result = json.loads(result.stdout)

                for dir_node in self.program_dir_walk_result:
                    if dir_node['root'] == '/'.join([self.program_dir, "log"]):
                        for idx, f in enumerate(dir_node['files']):
                            file_name = f
                            file_path = '/'.join([dir_node['root'], f])
                            time_stamp = f.split('-')[0]
                            file_name_display = f.split('-')[1]

                            _date = time_stamp.split('T')[0]
                            _time = time_stamp.split('T')[1]
                            year = _date[:4]
                            month = _date[4:6]
                            day = _date[6:]
                            date = '-'.join([year, month, day])

                            if '+' in _time:
                                __time = _time.split('+')[0].split('.')[0]
                                hour = __time[:2]
                                mins = __time[2:4]
                                sec = __time[4:]
                                gmt = _time.split('+')[1]
                                gmt = '+'+gmt
                            elif '-' in _time:
                                __time = _time.split('-')[0].split('.')[0]
                                hour = __time[:2]
                                mins = __time[2:4]
                                sec = __time[4:]
                                gmt = _time.split('-')[1]
                                gmt = '-'+gmt
                            time = ':'.join([hour, mins, sec])
                            time = time+' '+gmt
                            '''
                            print "FILE NAME="+file_name
                            print "FILE PATH="+file_path
                            print "TIMESTAMP="+time_stamp
                            print "FILE NAME DISPLAY="+file_name_display
                            print "DATE="+date
                            print "TIME="+time
                            print "========================================="
                            '''

                            parent = self.tree_logs_model.findItems(date)
                            if parent:
                                if file_name_display.split('.')[0] == "stdout":
                                    parent[0].child(0).appendRow([QStandardItem(file_name_display),
                                                                  QStandardItem(time),
                                                                  QStandardItem("LOG_FILE"),
                                                                  QStandardItem(file_path)])
                                elif file_name_display.split('.')[0] == "stderr":
                                    parent[0].child(1).appendRow([QStandardItem(file_name_display),
                                                                  QStandardItem(time),
                                                                  QStandardItem("LOG_FILE"),
                                                                  QStandardItem(file_path)])
                            else:
                                parent = [QStandardItem(date), QStandardItem("")]
                                parent[0].appendRow([QStandardItem("STDOUT"), QStandardItem("")])
                                parent[0].appendRow([QStandardItem("STDERR"), QStandardItem("")])
                                if file_name_display.split('.')[0] == "stdout":
                                    parent[0].child(0).appendRow([QStandardItem(file_name_display),
                                                                  QStandardItem(time),
                                                                  QStandardItem("LOG_FILE"),
                                                                  QStandardItem(file_path)])
                                elif file_name_display.split('.')[0] == "stderr":
                                    parent[0].child(1).appendRow([QStandardItem(file_name_display),
                                                                  QStandardItem(time),
                                                                  QStandardItem("LOG_FILE"),
                                                                  QStandardItem(file_path)])
                                parent[0].setSelectable(False)
                                parent[1].setSelectable(False)
                                parent[0].child(0, 0).setSelectable(False)
                                parent[0].child(0, 1).setSelectable(False)
                                parent[0].child(1, 0).setSelectable(False)
                                parent[0].child(1, 1).setSelectable(False)
                                self.tree_logs_model.appendRow(parent)

                # Enable/Disable Download and Delete buttons based on available data
                self.button_download_log.setEnabled(self.tree_logs_model.rowCount())
                self.button_delete_log.setEnabled(self.tree_logs_model.rowCount())
            else:
                # TODO: Error popup for user?
                print result

        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)

        self.script_manager.execute_script('program_get_os_walk',
                                           cb_program_get_os_walk,
                                           [self.program_dir])

        # arguments
        arguments = []
        editable_arguments_offset = max(self.program.cast_custom_option_value('editable_arguments_offset', int, 0), 0)

        for argument in self.program.arguments.items[editable_arguments_offset:]:
            arguments.append(unicode(argument))

        self.label_arguments.setText('\n'.join(arguments))

        environment = []
        editable_environment_offset = max(self.program.cast_custom_option_value('editable_environment_offset', int, 0), 0)

        for variable in self.program.environment.items[editable_environment_offset:]:
            environment.append(unicode(variable))

        self.label_environment.setText('\n'.join(environment))

        # stdio
        stdin_redirection_file  = self.program.stdin_redirection  == REDProgram.STDIO_REDIRECTION_FILE
        stdout_redirection_file = self.program.stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE
        stderr_redirection_file = self.program.stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE

        self.label_stdin_source.setText(Constants.api_stdin_redirection_display_names.get(self.program.stdin_redirection, '<unknown>'))
        self.label_stdin_file_title.setVisible(stdin_redirection_file)
        self.label_stdin_file.setVisible(stdin_redirection_file)

        if stdin_redirection_file:
            self.label_stdin_file.setText(unicode(self.program.stdin_file_name))

        self.label_stdout_target.setText(Constants.api_stdout_redirection_display_names.get(self.program.stdout_redirection, '<unknown>'))
        self.label_stdout_file_title.setVisible(stdout_redirection_file)
        self.label_stdout_file.setVisible(stdout_redirection_file)

        if stdout_redirection_file:
            self.label_stdout_file.setText(unicode(self.program.stdout_file_name))

        self.label_stderr_target.setText(Constants.api_stderr_redirection_display_names.get(self.program.stderr_redirection, '<unknown>'))
        self.label_stderr_file_title.setVisible(stderr_redirection_file)
        self.label_stderr_file.setVisible(stderr_redirection_file)

        if stderr_redirection_file:
            self.label_stderr_file.setText(unicode(self.program.stderr_file_name))

    def download_selected_log(self):
        index_list =  self.tree_logs.selectedIndexes()
        print len(index_list)

        if len(index_list) == 0 or len(index_list) % 4 != 0:
            return

        index_list_chunked =  zip(*[iter(index_list)] * 4)
        if index_list_chunked <= 0:
            return
        global log_files_to_process
        log_files_to_process = len(index_list_chunked)

        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.Directory)
        file_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        global log_files_download_dir
        log_files_download_dir = file_dialog.getExistingDirectory(self,
                                                             "Download Log Files")

        print log_files_download_dir

        for chunk in index_list_chunked:
            if self.tree_logs_model.itemFromIndex(chunk[2]).text() != "LOG_FILE":
                return
            log_filename = unicode(self.tree_logs_model.itemFromIndex(chunk[3]).text())
            print 'download_selected_log', log_filename

    def delete_selected_log(self):
        #selected_items = self.list_logs.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'delete_selected_log', filename

    def upload_files(self):
        print 'upload_files'

    def download_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'download_selected_files', filenames

    def rename_selected_file(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'rename_selected_file', filename

    def delete_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'delete_selected_files', filenames

    def set_edit_buttons_enabled(self, enabled):
        self.button_edit_general.setEnabled(enabled)
        self.button_edit_language.setEnabled(enabled)
        self.button_edit_arguments.setEnabled(enabled)
        self.button_edit_stdio.setEnabled(enabled)
        self.button_edit_schedule.setEnabled(enabled)

    def show_edit_general_wizard(self):
        self.set_edit_buttons_enabled(False)

        self.edit_general_wizard = ProgramWizardEdit(self.session, self.program, [], self.script_manager)
        self.edit_general_wizard.setPage(Constants.PAGE_GENERAL, ProgramPageGeneral())
        self.edit_general_wizard.finished.connect(self.edit_general_wizard_finished)
        self.edit_general_wizard.show()

    def edit_general_wizard_finished(self, result):
        self.edit_general_wizard.finished.disconnect(self.edit_general_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_general_wizard.page(Constants.PAGE_GENERAL).apply_program_changes()
            self.refresh_info()
            self.name_changed.emit()

        self.set_edit_buttons_enabled(True)

    def show_edit_language_wizard(self):
        print 'show_edit_language_wizard'

    def show_edit_arguments_wizard(self):
        self.set_edit_buttons_enabled(False)

        self.edit_arguments_wizard = ProgramWizardEdit(self.session, self.program, [], self.script_manager)
        self.edit_arguments_wizard.setPage(Constants.PAGE_ARGUMENTS, ProgramPageArguments())
        self.edit_arguments_wizard.finished.connect(self.edit_arguments_wizard_finished)
        self.edit_arguments_wizard.show()

    def edit_arguments_wizard_finished(self, result):
        self.edit_arguments_wizard.finished.disconnect(self.edit_arguments_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_arguments_wizard.page(Constants.PAGE_ARGUMENTS).apply_program_changes()
            self.refresh_info()

        self.set_edit_buttons_enabled(True)

    def show_edit_stdio_wizard(self):
        self.set_edit_buttons_enabled(False)

        self.edit_stdio_wizard = ProgramWizardEdit(self.session, self.program, [], self.script_manager)
        self.edit_stdio_wizard.setPage(Constants.PAGE_STDIO, ProgramPageStdio())
        self.edit_stdio_wizard.finished.connect(self.edit_stdio_wizard_finished)
        self.edit_stdio_wizard.show()

    def edit_stdio_wizard_finished(self, result):
        self.edit_stdio_wizard.finished.disconnect(self.edit_stdio_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_stdio_wizard.page(Constants.PAGE_STDIO).apply_program_changes()
            self.refresh_info()

        self.set_edit_buttons_enabled(True)

    def show_edit_schedule_wizard(self):
        print 'show_edit_schedule_wizard'
