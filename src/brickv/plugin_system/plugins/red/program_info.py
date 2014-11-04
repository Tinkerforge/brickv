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
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem, QDialog, QFileDialog, QProgressDialog, QMessageBox
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_wizard_edit import ProgramWizardEdit
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.program_page_general import ProgramPageGeneral
from brickv.plugin_system.plugins.red.program_page_c import ProgramPageC
from brickv.plugin_system.plugins.red.program_page_csharp import ProgramPageCSharp
from brickv.plugin_system.plugins.red.program_page_delphi import ProgramPageDelphi
from brickv.plugin_system.plugins.red.program_page_java import ProgramPageJava
from brickv.plugin_system.plugins.red.program_page_javascript import ProgramPageJavaScript
from brickv.plugin_system.plugins.red.program_page_octave import ProgramPageOctave
from brickv.plugin_system.plugins.red.program_page_perl import ProgramPagePerl
from brickv.plugin_system.plugins.red.program_page_php import ProgramPagePHP
from brickv.plugin_system.plugins.red.program_page_python import ProgramPagePython
from brickv.plugin_system.plugins.red.program_page_ruby import ProgramPageRuby
from brickv.plugin_system.plugins.red.program_page_shell import ProgramPageShell
from brickv.plugin_system.plugins.red.program_page_vbnet import ProgramPageVBNET
from brickv.plugin_system.plugins.red.program_page_arguments import ProgramPageArguments
from brickv.plugin_system.plugins.red.program_page_stdio import ProgramPageStdio
from brickv.plugin_system.plugins.red.program_page_schedule import ProgramPageSchedule
from brickv.plugin_system.plugins.red.ui_program_info import Ui_ProgramInfo
from brickv.async_call import async_call
import os
import json

def expand_directory_walk_to_files_list(directory_walk):
    files = []

    def expand(root, dw):
        if 'c' in dw:
            for child_name, child_dw in dw['c'].iteritems():
                expand(os.path.join(root, child_name), child_dw)
        else:
            files.append(root)

    expand('', directory_walk)

    return files


def expand_directory_walk_to_model(directory_walk, parent):
    model = QStandardItemModel(parent)

    def expand(parent_item, name, dw):
        if 'c' in dw:
            if name == None:
                item = parent_item
            else:
                item = QStandardItem(name)
                parent_item.appendRow([item, QStandardItem(''), QStandardItem('')])

            for child_name, child_dw in dw['c'].iteritems():
                expand(item, child_name, child_dw)
        else:
            parent_item.appendRow([QStandardItem(name), QStandardItem(unicode(dw['s'])), QStandardItem(unicode(dw['l']))])

    expand(model.invisibleRootItem(), None, directory_walk)

    return model


class ProgramInfo(QWidget, Ui_ProgramInfo):
    name_changed = pyqtSignal()

    def __init__(self, session, script_manager, image_version_ref, executable_versions, program, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session             = session
        self.script_manager      = script_manager
        self.image_version_ref   = image_version_ref
        self.executable_versions = executable_versions
        self.program             = program
        self.root_directory      = unicode(self.program.root_directory)

        self.program.scheduler_state_changed_callback = self.scheduler_state_changed
        self.program.process_spawned_callback = self.process_spawned

        self.program_refresh_in_progress = False
        self.logs_refresh_in_progress = False
        self.files_refresh_in_progress = False

        self.available_files = []
        self.available_directories = []

        self.edit_general_wizard = None
        self.edit_language_wizard = None
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

        self.button_kill.clicked.connect(self.kill_process)
        self.button_schedule_now.clicked.connect(self.schedule_now)
        self.button_send_stdin_pipe_input.clicked.connect(self.send_stdin_pipe_input)

        self.check_show_environment.stateChanged.connect(self.update_ui_state)

        self.button_edit_general.clicked.connect(self.show_edit_general_wizard)
        self.button_edit_language.clicked.connect(self.show_edit_language_wizard)
        self.button_edit_arguments.clicked.connect(self.show_edit_arguments_wizard)
        self.button_edit_stdio.clicked.connect(self.show_edit_stdio_wizard)
        self.button_edit_schedule.clicked.connect(self.show_edit_schedule_wizard)

        self.update_ui_state()

    def scheduler_state_changed(self, program):
        self.update_ui_state()

    def process_spawned(self, program):
        self.update_ui_state()

        self.program.last_spawned_process.state_changed_callback = self.process_state_changed

    def process_state_changed(self, process):
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

            if result == None or result.stderr != "":
                self.update_ui_state()
                # TODO: Error popup for user?
                print result
                return

            self.program_dir_walk_result = json.loads(result.stdout)

            for dir_node in self.program_dir_walk_result:
                if dir_node['root'] == os.path.join(self.program_dir, "log"):
                    for idx, f in enumerate(dir_node['files']):
                        file_name = f['name']
                        file_size = unicode(f['size'])
                        file_path = os.path.join(dir_node['root'], file_name)
                        if len(file_name.split('-')) < 2:
                            continue

                        if file_name.split('-')[0] == "continuous":
                            parent_continuous = None
                            for i in range(self.tree_logs_model.rowCount()):
                                if self.tree_logs_model.item(i).text() == "Continuous":
                                    parent_continuous = self.tree_logs_model.item(i)
                                    parent_continuous_size = self.tree_logs_model.item(i, 1)
                                    break

                            if parent_continuous:
                                if file_name.split('-')[1] == "stdout.log":
                                    parent_continuous.appendRow([QStandardItem("stdout"),
                                                                 QStandardItem(file_size),
                                                                 QStandardItem("LOG_FILE_CONT"),
                                                                 QStandardItem(file_path)])
                                elif file_name.split('-')[1] == "stderr.log":
                                    parent_continuous.appendRow([QStandardItem("stderr"),
                                                                 QStandardItem(file_size),
                                                                 QStandardItem("LOG_FILE_CONT"),
                                                                 QStandardItem(file_path)])
                                current_size = int(parent_continuous_size.text())
                                new_file_size = int(file_size)
                                parent_continuous_size.setText(unicode(current_size + new_file_size))
                            else:
                                parent_continuous = [QStandardItem("Continuous"),
                                                     QStandardItem(file_size),
                                                     QStandardItem("PARENT_CONT"),
                                                     QStandardItem("")]
                                if file_name.split('-')[1] == "stdout.log":
                                    parent_continuous[0].appendRow([QStandardItem("stdout"),
                                                                    QStandardItem(file_size),
                                                                    QStandardItem("LOG_FILE_CONT"),
                                                                    QStandardItem(file_path)])
                                elif file_name.split('-')[1] == "stderr.log":
                                    parent_continuous[0].appendRow([QStandardItem("stderr"),
                                                                    QStandardItem(file_size),
                                                                    QStandardItem("LOG_FILE_CONT"),
                                                                    QStandardItem(file_path)])
                                self.tree_logs_model.appendRow(parent_continuous)

                            self.tree_logs_model.sort(0, Qt.DescendingOrder)
                            self.update_ui_state()
                            continue

                        time_stamp = file_name.split('-')[0]
                        file_name_display = file_name.split('-')[1]

                        if len(time_stamp.split('T')) < 2:
                            continue
                        _date = time_stamp.split('T')[0]
                        _time = time_stamp.split('T')[1]
                        year = _date[:4]
                        month = _date[4:6]
                        day = _date[6:]
                        date = '-'.join([year, month, day])

                        if '+' in _time:
                            if len(_time.split('+')) < 2:
                                continue
                            __time = _time.split('+')[0].split('.')[0]
                            hour = __time[:2]
                            mins = __time[2:4]
                            sec = __time[4:]
                            gmt = _time.split('+')[1]
                            gmt = '+'+gmt
                        elif '-' in _time:
                            if len(_time.split('-')) < 2:
                                continue
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
                                    parent_date.child(i, 1).setText(unicode(current_size + new_file_size))

                                    current_size = int(parent_date_size.text())
                                    new_file_size = int(parent_date.child(i, 1).text())
                                    parent_date_size.setText(unicode(current_size + new_file_size))
                                    break

                            if not found_parent_time:
                                parent_date.appendRow([QStandardItem(time),
                                                       QStandardItem(file_size),
                                                       QStandardItem("PARENT_TIME"),
                                                       QStandardItem("")])
                                parent_date.child(parent_date.rowCount()-1).appendRow([QStandardItem(file_name_display),
                                                                                       QStandardItem(file_size),
                                                                                       QStandardItem("LOG_FILE"),
                                                                                       QStandardItem(file_path)])
                                current_size = int(parent_date_size.text())
                                new_file_size = int(file_size)
                                parent_date_size.setText(unicode(current_size + new_file_size))

                        else:
                            parent_date = [QStandardItem(date),
                                           QStandardItem(file_size),
                                           QStandardItem("PARENT_DATE"),
                                           QStandardItem("")]
                            parent_date[0].appendRow([QStandardItem(time),
                                                      QStandardItem(file_size),
                                                      QStandardItem("PARENT_TIME"),
                                                      QStandardItem("")])
                            parent_date[0].child(0).appendRow([QStandardItem(file_name_display),
                                                               QStandardItem(file_size),
                                                               QStandardItem("LOG_FILE"),
                                                               QStandardItem(file_path)])
                            self.tree_logs_model.appendRow(parent_date)

            self.tree_logs_model.sort(0, Qt.DescendingOrder)
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
            if result == None or len(result.stderr) > 0:
                self.files_refresh_in_progress = False
                self.update_ui_state()
                return # FIXME: report error

            def expand_async(data):
                directory_walk = json.loads(data)
                available_files = []
                available_directories = []

                if directory_walk != None:
                    available_files = sorted(expand_directory_walk_to_files_list(directory_walk))
                    directories = set()

                    for available_file in available_files:
                        directory = os.path.split(available_file)[0]

                        if len(directory) > 0:
                            directories.add(directory)

                    available_directories = sorted(list(directories))

                return directory_walk, available_files, available_directories

            def cb_expand_success(args):
                directory_walk, available_files, available_directories = args

                self.available_files = available_files
                self.available_directories = available_directories
                self.files_refresh_in_progress = False
                self.update_ui_state()

                self.tree_files.setModel(expand_directory_walk_to_model(directory_walk, self))

            def cb_expand_error():
                pass # FIXME: report error

            async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

        self.files_refresh_in_progress = True
        self.update_ui_state()

        self.script_manager.execute_script('directory_walk', cb_directory_walk,
                                           [os.path.join(self.root_directory, 'bin')],
                                           max_len=1024*1024)

    def update_ui_state(self):
        self.set_widget_enabled(self.button_download_logs, self.tree_logs_model.rowCount() > 0)
        self.set_widget_enabled(self.button_delete_logs, self.tree_logs_model.rowCount() > 0)
        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)

        #has_files_selection = len(self.tree_files.selectedItems()) > 0
        #self.set_widget_enabled(self.button_download_files, has_files_selection)
        #self.set_widget_enabled(self.button_rename_file, len(self.tree_files.selectedItems()) == 1)
        #self.set_widget_enabled(self.button_delete_files, has_files_selection)

        if self.program_refresh_in_progress or self.files_refresh_in_progress or self.logs_refresh_in_progress:
            self.button_refresh.setText('Refreshing...')
            self.set_edit_buttons_enabled(False)
        else:
            self.button_refresh.setText('Refresh')
            self.set_edit_buttons_enabled(True)

        # general
        name              = self.program.cast_custom_option_value('name', unicode, '<unknown>')
        language_api_name = self.program.cast_custom_option_value('language', unicode, '<unknown>')
        description       = self.program.cast_custom_option_value('description', unicode, '')

        try:
            language_display_name = Constants.get_language_display_name(language_api_name)
        except:
            language_display_name = '<unknown>'

        self.label_name.setText(name)
        self.label_identifier.setText(unicode(self.program.identifier))
        self.label_language.setText(language_display_name)
        self.label_description.setText(description)

        # status
        process_running = False

        if self.program.last_spawned_process != None:
            timestamp = self.program.last_spawned_process.timestamp
            date      = QDateTime.fromTime_t(timestamp).toString('yyyy-MM-dd')
            time      = QDateTime.fromTime_t(timestamp).toString('HH:mm:ss')

            if self.program.last_spawned_process.state == REDProcess.STATE_UNKNOWN:
                self.label_program_current_state.setText('Unknown since {0} at {1}'.format(date, time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_RUNNING:
                self.label_program_current_state.setText('Running since {0} at {1}'.format(date, time))
                process_running = True
            elif self.program.last_spawned_process.state == REDProcess.STATE_ERROR:
                if self.program.last_spawned_process.exit_code == REDProcess.E_INTERNAL_ERROR:
                    self.label_program_current_state.setText('Internal error occurred on {0} at {1}'.format(date, time))
                elif self.program.last_spawned_process.exit_code == REDProcess.E_CANNOT_EXECUTE:
                    self.label_program_current_state.setText('Could not be executed on {0} at {1}'.format(date, time))
                elif self.program.last_spawned_process.exit_code == REDProcess.E_DOES_NOT_EXIST:
                    self.label_program_current_state.setText('Executable does not exist on {0} at {1}'.format(date, time))
                else:
                    self.label_program_current_state.setText('Unknown error occurred on {0} at {1}'.format(date, time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_EXITED:
                if self.program.last_spawned_process.exit_code == 0:
                    self.label_program_current_state.setText('Not running, last run exited normally on {0} at {1}'.format(date, time))
                else:
                    self.label_program_current_state.setText('Not running, last run exited with an error (exit code: {0}) on {1} at {2}'
                                                            .format(self.program.last_spawned_process.exit_code, date, time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_KILLED:
                    self.label_program_current_state.setText('Not running, last run was killed (signal: {0}) on {1} at {2}'
                                                             .format(self.program.last_spawned_process.exit_code, date, time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_STOPPED:
                self.label_program_current_state.setText('Stopped on {0} at {1}'.format(date, time)) # FIXME: show continue button?

            self.label_last_start.setText(QDateTime.fromTime_t(self.program.last_spawned_timestamp).toString('yyyy-MM-dd HH:mm:ss'))
        else:
            self.label_program_current_state.setText('Not running')
            self.label_last_start.setText('Never started')

        scheduler_state_display_name = Constants.api_scheduler_state_display_name.get(self.program.scheduler_state, '<unknown>')

        if self.program.scheduler_state == REDProgram.SCHEDULER_STATE_STOPPED:
            if process_running:
                scheduler_state_display_name += ', no automatic program repeat'
            else:
                scheduler_state_display_name += ', no automatic program start'

        self.label_scheduler_current_state.setText(scheduler_state_display_name)
        self.label_last_scheduler_state_change.setText(QDateTime.fromTime_t(self.program.scheduler_timestamp).toString('yyyy-MM-dd HH:mm:ss'))

        if self.program.scheduler_message != None:
            self.label_last_scheduler_message.setText(unicode(self.program.scheduler_message))
        else:
            self.label_last_scheduler_message.setText('None')

        self.set_widget_enabled(self.button_kill, process_running)
        self.set_widget_enabled(self.button_schedule_now, not process_running)

        # language
        self.group_language.setTitle('{0} Configuration'.format(language_display_name))

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

        show_environment = self.check_show_environment.checkState() == Qt.Checked

        self.label_environment_title.setVisible(show_environment)
        self.label_environment.setVisible(show_environment)
        self.label_environment.setText('\n'.join(environment))

        # stdio
        stdin_redirection_pipe  = self.program.stdin_redirection  == REDProgram.STDIO_REDIRECTION_PIPE
        stdin_redirection_file  = self.program.stdin_redirection  == REDProgram.STDIO_REDIRECTION_FILE
        stdout_redirection_file = self.program.stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE
        stderr_redirection_file = self.program.stderr_redirection == REDProgram.STDIO_REDIRECTION_FILE

        self.label_stdin_source.setText(Constants.api_stdin_redirection_display_names.get(self.program.stdin_redirection, '<unknown>'))
        self.label_stdin_pipe_input_title.setVisible(stdin_redirection_pipe)
        self.edit_stdin_pipe_input.setVisible(stdin_redirection_pipe)
        self.button_send_stdin_pipe_input.setVisible(stdin_redirection_pipe)
        self.label_stdin_file_title.setVisible(stdin_redirection_file)
        self.label_stdin_file.setVisible(stdin_redirection_file)

        self.set_widget_enabled(self.edit_stdin_pipe_input, process_running)
        self.set_widget_enabled(self.button_send_stdin_pipe_input, process_running)

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
        start_condition_cron   = self.program.start_condition == REDProgram.START_CONDITION_CRON

        self.label_start_condition.setText(Constants.api_start_condition_display_names.get(self.program.start_condition, '<unknown>'))
        self.label_start_time_title.setVisible(start_condition_time)
        self.label_start_time.setVisible(start_condition_time)
        self.label_start_time.setText(QDateTime.fromTime_t(self.program.start_timestamp).toString('yyyy-MM-dd HH:mm:ss'))
        self.label_start_delay_title.setVisible(start_condition_now or start_condition_reboot)
        self.label_start_delay.setVisible(start_condition_now or start_condition_reboot)
        self.label_start_delay.setText('{0} seconds'.format(self.program.start_delay))
        self.label_start_fields_title.setVisible(start_condition_cron)
        self.label_start_fields.setVisible(start_condition_cron)

        if start_condition_cron:
            self.label_start_fields.setText(unicode(self.program.start_fields))

        repeat_mode_never    = self.program.repeat_mode == REDProgram.REPEAT_MODE_NEVER
        repeat_mode_interval = self.program.repeat_mode == REDProgram.REPEAT_MODE_INTERVAL
        repeat_mode_cron     = self.program.repeat_mode == REDProgram.REPEAT_MODE_CRON

        self.label_repeat_mode.setText(Constants.api_repeat_mode_display_names.get(self.program.repeat_mode, '<unknown>'))
        self.label_repeat_interval_title.setVisible(repeat_mode_interval)
        self.label_repeat_interval.setVisible(repeat_mode_interval)
        self.label_repeat_interval.setText('{0} seconds'.format(self.program.repeat_interval))
        self.label_repeat_fields_title.setVisible(repeat_mode_cron)
        self.label_repeat_fields.setVisible(repeat_mode_cron)

        if repeat_mode_cron:
            self.label_repeat_fields.setText(unicode(self.program.repeat_fields))

    def load_log_files_for_ops(self, index_list):
        if len(index_list) % 4 != 0:
            return False

        index_list_chunked = zip(*[iter(index_list)] * 4)
        logs_download_dict = {'files': {}, 'total_download_size': 0}

        def populate_log_download(item_list):
            if item_list[2].text() == "PARENT_CONT":
                for i in range(item_list[0].rowCount()):
                    f_size = int(item_list[0].child(i, 1).text()) # File size
                    f_path = unicode(item_list[0].child(i, 3).text()) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] = \
                            logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "PARENT_DATE":
                for i in range(item_list[0].rowCount()):
                    parent_time = item_list[0].child(i)
                    for j in range(parent_time.rowCount()):
                        f_size = int(parent_time.child(j, 1).text()) # File size
                        f_path = unicode(parent_time.child(j, 3).text()) # File path
                        if not f_path in logs_download_dict['files']:
                            logs_download_dict['files'][f_path] = {'size': f_size}
                            logs_download_dict['total_download_size'] = \
                                logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "PARENT_TIME":
                for i in range(item_list[0].rowCount()):
                    f_size = int(item_list[0].child(i, 1).text()) # File size
                    f_path = unicode(item_list[0].child(i, 3).text()) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] = \
                            logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "LOG_FILE" or \
                 item_list[2].text() == "LOG_FILE_CONT":
                f_size = int(item_list[1].text()) # File size
                f_path = unicode(item_list[3].text()) # File path
                if not f_path in logs_download_dict['files']:
                    logs_download_dict['files'][f_path] = {'size': f_size}
                    logs_download_dict['total_download_size'] = \
                        logs_download_dict['total_download_size'] + f_size
            else:
                pass

        for index_chunk in index_list_chunked:
            item_list = []
            for index in index_chunk:
                item = self.tree_logs_model.itemFromIndex(index)
                item_list.append(item)
            populate_log_download(item_list)

        return logs_download_dict

    def download_selected_logs(self):
        def log_download_pd_closed():
            if len(log_files_to_download['files']) > 0:
                QtGui.QMessageBox.warning(None,
                                          'Program | Logs',
                                          'Download could not finish.',
                                          QtGui.QMessageBox.Ok)
            else:
                QtGui.QMessageBox.information(None,
                                              'Program | Logs',
                                              'Download complete!',
                                              QtGui.QMessageBox.Ok)

        self.tree_logs.setColumnHidden(2, False)
        self.tree_logs.setColumnHidden(3, False)
        index_list =  self.tree_logs.selectedIndexes()
        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)
        if not index_list:
            return

        log_files_to_download = self.load_log_files_for_ops(index_list)
        if not log_files_to_download:
            return

        log_files_download_dir = unicode(QFileDialog.getExistingDirectory(self, "Choose Download Location"))

        if log_files_download_dir != "":
            log_download_pd = QProgressDialog(str(len(log_files_to_download['files']))+" file(s) remaining...",
                                              "Cancel",
                                              0,
                                              100,
                                              self)
            log_download_pd.setWindowTitle("Download Progress")
            log_download_pd.setAutoReset(False)
            log_download_pd.setAutoClose(False)
            log_download_pd.setMinimumDuration(0)
            log_download_pd.setValue(0)

            log_download_pd.canceled.connect(log_download_pd_closed)

            def cb_open(red_file):
                def cb_read_status(bytes_read, max_length):
                    files_remaining = str(len(log_files_to_download['files']))
                    current_percent = int(float(bytes_read)/float(max_length) * 100)

                    log_download_pd.setLabelText(files_remaining+" file(s) remaining...")
                    log_download_pd.setValue(current_percent)

                    if current_percent == 100:
                        log_download_pd.setValue(0)

                def cb_read(red_file, result):
                    red_file.release()
                    if result is not None:
                        # Success
                        read_file_path = log_files_to_download['files'].keys()[0]
                        save_file_name = ''.join(read_file_path.split('/')[-1:])
                        with open(os.path.join(unicode(log_files_download_dir),
                                               unicode(save_file_name)),
                                               'wb') as fh_log_write:
                            fh_log_write.write(result.data)

                        if read_file_path in log_files_to_download['files']:
                            log_files_to_download['files'].pop(read_file_path, None)

                        if len(log_files_to_download['files']) == 0:
                            log_download_pd.close()
                            return

                        if not log_download_pd.wasCanceled():
                            log_download_pd.setLabelText(str(len(log_files_to_download['files']))+" file(s) remaining...")
                            log_download_pd.setValue(0)
                            async_call(REDFile(self.session).open,
                                       (log_files_to_download['files'].keys()[0],
                                       REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                                       cb_open,
                                       cb_open_error)

                    else:
                        # TODO: Error popup for user?
                        log_download_pd.close()
                        print result

                red_file.read_async(log_files_to_download['files'].values()[0]['size'],
                                    lambda x: cb_read(red_file, x),
                                    cb_read_status)

            def cb_open_error(result):
                # TODO: Error popup for user?
                log_download_pd.close()
                print result

            if len(log_files_to_download['files']) > 0:
                async_call(REDFile(self.session).open,
                           (log_files_to_download['files'].keys()[0],
                           REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                           cb_open,
                           cb_open_error)

    def delete_selected_logs(self):
        def cb_program_delete_logs(result):
            if result.stderr == "":
                if json.loads(result.stdout):
                    QtGui.QMessageBox.information(None,
                                                  'Program | Logs',
                                                  'Deleted successfully!',
                                                  QtGui.QMessageBox.Ok)
                else:
                    QtGui.QMessageBox.critical(None,
                                               'Program | Logs',
                                               'Deletion failed',
                                               QtGui.QMessageBox.Ok)
            else:
                pass
                # TODO: Error popup for user?

        self.tree_logs.setColumnHidden(2, False)
        self.tree_logs.setColumnHidden(3, False)
        index_list =  self.tree_logs.selectedIndexes()
        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)
        if not index_list:
            return

        log_files_to_delete = self.load_log_files_for_ops(index_list)

        if not log_files_to_delete:
            return

        file_list = []

        for f_path in log_files_to_delete['files']:
            file_list.append(f_path)

        if len(file_list) > 0:
            self.script_manager.execute_script('program_delete_logs',
                                               cb_program_delete_logs,
                                               [json.dumps(file_list)])

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

    def kill_process(self):
        if self.program.last_spawned_process != None:
            try:
                self.program.last_spawned_process.kill(REDProcess.SIGNAL_KILL)
            except REDError as e:
                QMessageBox.critical(self, 'Kill Error',
                                     u'Could not kill current process of program [{0}]:\n\n{1}'
                                     .format(self.program.cast_custom_option_value('name', unicode, '<unknown>'), str(e)))

    def schedule_now(self):
        try:
            self.program.schedule_now()
        except REDError as e:
            QMessageBox.critical(self, 'Schedule Error',
                                 u'Could not schedule program [{0}] now:\n\n{1}'
                                 .format(self.program.cast_custom_option_value('name', unicode, '<unknown>'), str(e)))

    def send_stdin_pipe_input(self):
        if self.program.last_spawned_process != None and self.program.last_spawned_process.stdin != None:
            try:
                self.program.last_spawned_process.stdin.write_async((unicode(self.edit_stdin_pipe_input.text()) + u'\n').encode('utf-8'))
            except REDError as e:
                QMessageBox.critical(self, 'Pipe Input Error',
                                     u'Could not write to stdin of current process of program [{0}]:\n\n{1}'
                                     .format(self.program.cast_custom_option_value('name', unicode, '<unknown>'), str(e)))
            else:
                self.edit_stdin_pipe_input.setText('')

    def set_widget_enabled(self, widget, enabled):
        # store current scroll position
        position = self.scroll_area.verticalScrollBar().value()

        widget.setEnabled(enabled)

        # restore current scroll position, because en/disableing buttons
        # makes the scroll position jump for som reason
        self.scroll_area.verticalScrollBar().setValue(position)

    def set_edit_buttons_enabled(self, enabled):
        # store current scroll position
        position = self.scroll_area.verticalScrollBar().value()

        self.button_refresh.setEnabled(enabled)
        self.button_edit_general.setEnabled(enabled)
        self.button_edit_language.setEnabled(enabled)
        self.button_edit_arguments.setEnabled(enabled)
        self.button_edit_stdio.setEnabled(enabled)
        self.button_edit_schedule.setEnabled(enabled)

        # restore current scroll position, because en/disableing buttons
        # makes the scroll position jump for som reason
        self.scroll_area.verticalScrollBar().setValue(position)

    def show_edit_general_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref, self.executable_versions)

        self.edit_general_wizard = ProgramWizardEdit(context, self.program, self.available_files, self.available_directories)
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
        language_api_name = self.program.cast_custom_option_value('language', unicode, '<unknown>')

        try:
            language_page = Constants.get_language_page(language_api_name)
        except:
            return

        language_page_classes = {
            Constants.PAGE_C:          ProgramPageC,
            Constants.PAGE_CSHARP:     ProgramPageCSharp,
            Constants.PAGE_DELPHI:     ProgramPageDelphi,
            Constants.PAGE_JAVA:       ProgramPageJava,
            Constants.PAGE_JAVASCRIPT: ProgramPageJavaScript,
            Constants.PAGE_OCTAVE:     ProgramPageOctave,
            Constants.PAGE_PERL:       ProgramPagePerl,
            Constants.PAGE_PHP:        ProgramPagePHP,
            Constants.PAGE_PYTHON:     ProgramPagePython,
            Constants.PAGE_RUBY:       ProgramPageRuby,
            Constants.PAGE_SHELL:      ProgramPageShell,
            Constants.PAGE_VBNET:      ProgramPageVBNET
        }

        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref, self.executable_versions)

        self.edit_language_wizard = ProgramWizardEdit(context, self.program, self.available_files, self.available_directories)
        self.edit_language_wizard.setPage(language_page, language_page_classes[language_page]())
        self.edit_language_wizard.finished.connect(self.edit_language_wizard_finished)
        self.edit_language_wizard.show()

    def edit_language_wizard_finished(self, result):
        self.edit_language_wizard.finished.disconnect(self.edit_language_wizard_finished)

        if result == QDialog.Accepted:
            #self.edit_language_wizard.page(Constants.PAGE_language).apply_program_changes()
            self.refresh_info()

        self.set_edit_buttons_enabled(True)

    def show_edit_arguments_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref, self.executable_versions)

        self.edit_arguments_wizard = ProgramWizardEdit(context, self.program, self.available_files, self.available_directories)
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

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref, self.executable_versions)

        self.edit_stdio_wizard = ProgramWizardEdit(context, self.program, self.available_files, self.available_directories)
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
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version_ref, self.executable_versions)

        self.edit_schedule_wizard = ProgramWizardEdit(context, self.program, self.available_files, self.available_directories)
        self.edit_schedule_wizard.setPage(Constants.PAGE_SCHEDULE, ProgramPageSchedule())
        self.edit_schedule_wizard.finished.connect(self.edit_schedule_wizard_finished)
        self.edit_schedule_wizard.show()

    def edit_schedule_wizard_finished(self, result):
        self.edit_schedule_wizard.finished.disconnect(self.edit_schedule_wizard_finished)

        if result == QDialog.Accepted:
            self.edit_schedule_wizard.page(Constants.PAGE_SCHEDULE).apply_program_changes()
            self.refresh_info()

        self.set_edit_buttons_enabled(True)
