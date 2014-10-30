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

from PyQt4.QtCore import pyqtSignal, QDateTime
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
import os
import json

log_files_to_process = -1
log_files_download_dir = ""

def expand_directory_walk_to_files_list(directory_walk):
    files = []

    def expand(root, dw):
        if 'c' in dw:
            for cn, cdw in dw['c'].iteritems():
                expand(os.path.join(root, cn), cdw)
        else:
            files.append(root)

    expand('', directory_walk)

    return files

class ProgramInfo(QWidget, Ui_ProgramInfo):
    name_changed = pyqtSignal()

    def __init__(self, session, script_manager, image_version_ref, program, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session = session
        self.script_manager = script_manager
        self.image_version_ref = image_version_ref
        self.program = program
        self.root_directory = unicode(self.program.root_directory)
        self.program_refresh_in_progress = False
        self.logs_refresh_in_progress = False
        self.files_refresh_in_progress = False

        self.available_files = []
        self.available_directories = []

        self.edit_general_wizard = None
        self.edit_arguments_wizard = None
        self.edit_stdio_wizard = None
        self.edit_schedule_wizard = None

        self.program_dir = unicode(self.program.root_directory)
        self.program_dir_walk_result = None
        self.tree_logs_model = QStandardItemModel(self)
        self.tree_logs_header_labels = ["Date/Time", "Size (bytes)"]
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        self.tree_logs.setModel(self.tree_logs_model)

        self.button_refresh.clicked.connect(self.refresh_info)
        self.button_download_logs.clicked.connect(self.download_selected_logs)
        self.button_delete_logs.clicked.connect(self.delete_selected_logs)
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

    def refresh_info(self):
        self.refresh_program()
        self.refresh_logs()
        self.refresh_files()

    def refresh_program(self):
        def refresh_async():
            self.program.update()

        def cb_success():
            self.program_refresh_in_progress = False
            self.update_ui_state()

        def cb_error():
            pass # FIXME: report error

        self.program_refresh_in_progress = True
        self.update_ui_state()

        async_call(refresh_async, None, cb_success, cb_error)

    def refresh_logs(self):
        def cb_program_get_os_walk(result):
            self.logs_refresh_in_progress = False
            if result.stderr != "":
                # TODO: Error popup for user?
                print result
                return

            self.program_dir_walk_result = json.loads(result.stdout)

            for dir_node in self.program_dir_walk_result:
                if dir_node['root'] == '/'.join([self.program_dir, "log"]):
                    for idx, f in enumerate(dir_node['files']):
                        file_name = f['name']
                        file_size = str(f['size'])
                        file_path = '/'.join([dir_node['root'], file_name])
                        if len(file_name.split('-')) < 2:
                            return
                        time_stamp = file_name.split('-')[0]
                        file_name_display = file_name.split('-')[1]

                        if len(time_stamp.split('T')) < 2:
                            return
                        _date = time_stamp.split('T')[0]
                        _time = time_stamp.split('T')[1]
                        year = _date[:4]
                        month = _date[4:6]
                        day = _date[6:]
                        date = '-'.join([year, month, day])

                        if '+' in _time:
                            if len(_time.split('+')) < 2:
                                return
                            __time = _time.split('+')[0].split('.')[0]
                            hour = __time[:2]
                            mins = __time[2:4]
                            sec = __time[4:]
                            gmt = _time.split('+')[1]
                            gmt = '+'+gmt
                        elif '-' in _time:
                            if len(_time.split('-')) < 2:
                                return
                            __time = _time.split('-')[0].split('.')[0]
                            hour = __time[:2]
                            mins = __time[2:4]
                            sec = __time[4:]
                            gmt = _time.split('-')[1]
                            gmt = '-'+gmt
                        time = ':'.join([hour, mins, sec])
                        time_with_gmt = time+' '+gmt

                        parent_date = None
                        for i in range(self.tree_logs_model.rowCount()):
                            if self.tree_logs_model.item(i).text() == date:
                                parent_date = self.tree_logs_model.item(i)
                                parent_date_size = self.tree_logs_model.item(i, 1)
                                break

                        if parent_date:
                            found_parent_time = False
                            for i in range(parent_date.rowCount()):
                                if parent_date.child(i).text() == time:
                                    found_parent_time = True
                                    parent_date.child(i).appendRow([QStandardItem(file_name_display),
                                                                    QStandardItem(file_size),
                                                                    QStandardItem("LOG_FILE"),
                                                                    QStandardItem(file_path)])
                                    current_size = int (parent_date.child(i, 1).text())
                                    new_file_size = int(file_size)
                                    parent_date.child(i, 1).setText(str(current_size + new_file_size))

                                    current_size = int(parent_date_size.text())
                                    new_file_size = int(parent_date.child(i, 1).text())
                                    parent_date_size.setText(str(current_size + new_file_size))
                                    break

                            if not found_parent_time:
                                parent_date.appendRow([QStandardItem(time), QStandardItem(file_size)])
                                parent_date.child(parent_date.rowCount()-1).appendRow([QStandardItem(file_name_display),
                                                                                       QStandardItem(file_size),
                                                                                       QStandardItem("LOG_FILE"),
                                                                                       QStandardItem(file_path)])
                                current_size = int(parent_date_size.text())
                                new_file_size = int(file_size)
                                parent_date_size.setText(str(current_size + new_file_size))

                        else:
                            parent_date = [QStandardItem(date), QStandardItem(file_size)]
                            parent_date[0].appendRow([QStandardItem(time), QStandardItem(file_size)])
                            parent_date[0].child(0).appendRow([QStandardItem(file_name_display),
                                                               QStandardItem(file_size),
                                                               QStandardItem("LOG_FILE"),
                                                               QStandardItem(file_path)])
                            self.tree_logs_model.appendRow(parent_date)

            self.update_ui_state()


        self.logs_refresh_in_progress = True
        self.update_ui_state()

        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_header_labels)
        self.script_manager.execute_script('program_get_os_walk',
                                           cb_program_get_os_walk,
                                           [self.program_dir])

    def refresh_files(self):
        def cb_directory_walk(result):
            if len(result.stderr) > 0:
                return # FIXME: report error

            def expand_async(data):
                directory_walk = json.loads(data)
                available_files = []

                if directory_walk != None:
                    available_files = expand_directory_walk_to_files_list(directory_walk)
                return sorted(available_files)

            def cb_expand_success(available_files):
                self.available_files = available_files
                self.files_refresh_in_progress = False
                self.update_ui_state()

            def cb_expand_error():
                pass # FIXME: report error

            async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

        self.files_refresh_in_progress = True
        self.update_ui_state()

        self.script_manager.execute_script('directory_walk', cb_directory_walk,
                                           [os.path.join(self.root_directory, 'bin')], max_len=1024*1024)

    def update_ui_state(self):
        self.button_download_logs.setEnabled(self.tree_logs_model.rowCount())
        self.button_delete_logs.setEnabled(self.tree_logs_model.rowCount())

        has_files_selection = len(self.tree_files.selectedItems()) > 0
        self.button_download_files.setEnabled(has_files_selection)
        self.button_rename_file.setEnabled(len(self.tree_files.selectedItems()) == 1)
        self.button_delete_files.setEnabled(has_files_selection)

        if self.program_refresh_in_progress or self.files_refresh_in_progress or self.logs_refresh_in_progress:
            self.button_refresh.setText('Refreshing...')
            self.set_buttons_enabled(False)
        else:
            self.button_refresh.setText('Refresh')
            self.set_buttons_enabled(True)

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

        # schedule
        start_condition_never  = self.program.start_condition == REDProgram.START_CONDITION_NEVER
        start_condition_now    = self.program.start_condition == REDProgram.START_CONDITION_NOW
        start_condition_reboot = self.program.start_condition == REDProgram.START_CONDITION_REBOOT
        start_condition_time   = self.program.start_condition == REDProgram.START_CONDITION_TIMESTAMP

        self.label_start_condition.setText(Constants.api_start_condition_display_names.get(self.program.start_condition, '<unknown>'))
        self.label_start_time_title.setVisible(start_condition_time)
        self.label_start_time.setVisible(start_condition_time)
        self.label_start_time.setText(QDateTime.fromTime_t(self.program.start_timestamp).toString('dd.MM.yyyy HH:mm:ss'))
        self.label_start_delay_title.setVisible(start_condition_now or start_condition_reboot)
        self.label_start_delay.setVisible(start_condition_now or start_condition_reboot)
        self.label_start_delay.setText('{0} seconds'.format(self.program.start_delay))

        repeat_mode_never    = self.program.repeat_mode == REDProgram.REPEAT_MODE_NEVER
        repeat_mode_interval = self.program.repeat_mode == REDProgram.REPEAT_MODE_INTERVAL
        repeat_mode_cron     = self.program.repeat_mode == REDProgram.REPEAT_MODE_CRON

        self.label_repeat_mode.setText(Constants.api_repeat_mode_display_names.get(self.program.repeat_mode, '<unknown>'))
        self.label_repeat_interval_title.setVisible(repeat_mode_interval)
        self.label_repeat_interval.setVisible(repeat_mode_interval)
        self.label_repeat_interval.setText('{0} seconds'.format(self.program.repeat_interval))
        self.label_repeat_fields_title.setVisible(repeat_mode_cron)
        self.label_repeat_fields.setVisible(repeat_mode_cron)
        self.label_repeat_fields.setText(unicode(self.program.repeat_fields))

    def download_selected_logs(self):
        index_list =  self.tree_logs.selectedIndexes()

        print index_list

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

        for chunk in index_list_chunked:
            if self.tree_logs_model.itemFromIndex(chunk[2]).text() != "LOG_FILE":
                return
            log_filename = unicode(self.tree_logs_model.itemFromIndex(chunk[3]).text())
            print 'download_selected_logs', log_filename

    def delete_selected_logs(self):
        #selected_items = self.list_logs.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'delete_selected_logs', filename

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

    def set_buttons_enabled(self, enabled):
        self.button_refresh.setEnabled(enabled)
        self.button_edit_general.setEnabled(enabled)
        self.button_edit_language.setEnabled(enabled)
        self.button_edit_arguments.setEnabled(enabled)
        self.button_edit_stdio.setEnabled(enabled)
        self.button_edit_schedule.setEnabled(enabled)

    def show_edit_general_wizard(self):
        self.set_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref)

        self.edit_general_wizard = ProgramWizardEdit(context, self.program)
        self.edit_general_wizard.setPage(Constants.PAGE_GENERAL, ProgramPageGeneral())
        self.edit_general_wizard.finished.connect(self.edit_general_wizard_finished)
        self.edit_general_wizard.show()

    def edit_general_wizard_finished(self, result):
        self.edit_general_wizard.finished.disconnect(self.edit_general_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_general_wizard.page(Constants.PAGE_GENERAL).apply_program_changes()
            self.refresh_info()
            self.name_changed.emit()

        self.set_buttons_enabled(True)

    def show_edit_language_wizard(self):
        print 'show_edit_language_wizard'

    def show_edit_arguments_wizard(self):
        self.set_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref)

        self.edit_arguments_wizard = ProgramWizardEdit(context, self.program)
        self.edit_arguments_wizard.setPage(Constants.PAGE_ARGUMENTS, ProgramPageArguments())
        self.edit_arguments_wizard.finished.connect(self.edit_arguments_wizard_finished)
        self.edit_arguments_wizard.show()

    def edit_arguments_wizard_finished(self, result):
        self.edit_arguments_wizard.finished.disconnect(self.edit_arguments_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_arguments_wizard.page(Constants.PAGE_ARGUMENTS).apply_program_changes()
            self.refresh_info()

        self.set_buttons_enabled(True)

    def show_edit_stdio_wizard(self):
        self.set_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref)

        self.edit_stdio_wizard = ProgramWizardEdit(context, self.program)
        self.edit_stdio_wizard.setPage(Constants.PAGE_STDIO, ProgramPageStdio())
        self.edit_stdio_wizard.finished.connect(self.edit_stdio_wizard_finished)
        self.edit_stdio_wizard.show()

    def edit_stdio_wizard_finished(self, result):
        self.edit_stdio_wizard.finished.disconnect(self.edit_stdio_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_stdio_wizard.page(Constants.PAGE_STDIO).apply_program_changes()
            self.refresh_info()

        self.set_buttons_enabled(True)

    def show_edit_schedule_wizard(self):
        self.set_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref)

        self.edit_schedule_wizard = ProgramWizardEdit(context, self.program)
        self.edit_schedule_wizard.setPage(Constants.PAGE_SCHEDULE, ProgramPageSchedule())
        self.edit_schedule_wizard.finished.connect(self.edit_schedule_wizard_finished)
        self.edit_schedule_wizard.show()

    def edit_schedule_wizard_finished(self, result):
        self.edit_schedule_wizard.finished.disconnect(self.edit_schedule_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_schedule_wizard.page(Constants.PAGE_SCHEDULE).apply_program_changes()
            self.refresh_info()

        self.set_buttons_enabled(True)
