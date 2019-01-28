# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

program_info_main.py: Program Info Main Widget

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

from PyQt5.QtCore import pyqtSignal, QTimer
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox

from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_info import ProgramInfoContext
from brickv.plugin_system.plugins.red.program_info_files import ProgramInfoFiles
from brickv.plugin_system.plugins.red.program_info_logs import ProgramInfoLogs
from brickv.plugin_system.plugins.red.program_info_c import ProgramInfoC
from brickv.plugin_system.plugins.red.program_info_csharp import ProgramInfoCSharp
from brickv.plugin_system.plugins.red.program_info_delphi import ProgramInfoDelphi
from brickv.plugin_system.plugins.red.program_info_java import ProgramInfoJava
from brickv.plugin_system.plugins.red.program_info_javascript import ProgramInfoJavaScript
from brickv.plugin_system.plugins.red.program_info_octave import ProgramInfoOctave
from brickv.plugin_system.plugins.red.program_info_perl import ProgramInfoPerl
from brickv.plugin_system.plugins.red.program_info_php import ProgramInfoPHP
from brickv.plugin_system.plugins.red.program_info_python import ProgramInfoPython
from brickv.plugin_system.plugins.red.program_info_ruby import ProgramInfoRuby
from brickv.plugin_system.plugins.red.program_info_shell import ProgramInfoShell
from brickv.plugin_system.plugins.red.program_info_vbnet import ProgramInfoVBNET
from brickv.plugin_system.plugins.red.program_wizard import ProgramWizardContext
from brickv.plugin_system.plugins.red.program_wizard_edit import ProgramWizardEdit
from brickv.plugin_system.plugins.red.program_wizard_upload import ProgramWizardUpload
from brickv.plugin_system.plugins.red.program_wizard_download import ProgramWizardDownload
from brickv.plugin_system.plugins.red.program_utils import *
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
from brickv.plugin_system.plugins.red.ui_program_info_main import Ui_ProgramInfoMain
from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path

class ProgramInfoMain(QWidget, Ui_ProgramInfoMain):
    name_changed = pyqtSignal(object)
    status_changed = pyqtSignal(object)

    def __init__(self, session, script_manager, image_version, executable_versions, program):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session             = session
        self.script_manager      = script_manager
        self.image_version       = image_version
        self.executable_versions = executable_versions
        self.program             = program
        self.root_directory      = self.program.root_directory

        self.last_upload_files_wizard_directory = get_home_path()

        self.program.scheduler_state_changed_callback      = self.scheduler_state_changed
        self.program.lite_scheduler_state_changed_callback = self.lite_scheduler_state_changed
        self.program.process_spawned_callback              = self.process_spawned
        self.program.lite_process_spawned_callback         = self.lite_process_spawned

        if self.program.last_spawned_process != None:
            self.program.last_spawned_process.state_changed_callback = self.process_state_changed

        if self.program.last_spawned_lite_process != None:
            self.program.last_spawned_lite_process.state_changed_callback = self.lite_process_state_changed

        self.first_show_event            = True
        self.tab_is_alive                = True
        self.program_refresh_in_progress = False

        self.edit_general_wizard   = None
        self.edit_language_wizard  = None
        self.edit_arguments_wizard = None
        self.edit_stdio_wizard     = None
        self.edit_schedule_wizard  = None
        self.upload_files_wizard   = None
        self.download_wizard       = None

        self.button_refresh.clicked.connect(self.refresh_info)

        self.button_start_program.clicked.connect(self.start_program)
        self.button_exit_process.clicked.connect(self.exit_process)
        self.button_kill_process.clicked.connect(self.kill_process)
        self.button_continue_schedule.clicked.connect(self.continue_schedule)
        self.button_send_stdin_pipe_input.clicked.connect(self.send_stdin_pipe_input)

        self.check_show_environment.stateChanged.connect(self.update_ui_state)

        self.button_edit_general.clicked.connect(self.show_edit_general_wizard)
        self.button_edit_language.clicked.connect(self.show_edit_language_wizard)
        self.button_edit_arguments.clicked.connect(self.show_edit_arguments_wizard)
        self.button_edit_stdio.clicked.connect(self.show_edit_stdio_wizard)
        self.button_edit_schedule.clicked.connect(self.show_edit_schedule_wizard)

        # create language info widget
        language_api_name = self.program.cast_custom_option_value('language', str, '<unknown>')

        try:
            language = Constants.get_language(language_api_name)
        except:
            language = None

        if language != None:
            language_info_classes = {
                Constants.LANGUAGE_C:          ProgramInfoC,
                Constants.LANGUAGE_CSHARP:     ProgramInfoCSharp,
                Constants.LANGUAGE_DELPHI:     ProgramInfoDelphi,
                Constants.LANGUAGE_JAVA:       ProgramInfoJava,
                Constants.LANGUAGE_JAVASCRIPT: ProgramInfoJavaScript,
                Constants.LANGUAGE_OCTAVE:     ProgramInfoOctave,
                Constants.LANGUAGE_PERL:       ProgramInfoPerl,
                Constants.LANGUAGE_PHP:        ProgramInfoPHP,
                Constants.LANGUAGE_PYTHON:     ProgramInfoPython,
                Constants.LANGUAGE_RUBY:       ProgramInfoRuby,
                Constants.LANGUAGE_SHELL:      ProgramInfoShell,
                Constants.LANGUAGE_VBNET:      ProgramInfoVBNET
            }

            if language_info_classes[language] != None:
                context = ProgramInfoContext(self.session, self.script_manager, self.executable_versions, self.program)

                self.widget_language = language_info_classes[language](context)
                self.layout_language.addWidget(self.widget_language)
            else:
                self.widget_language = None
        else:
            self.widget_language = None

        self.current_language_action = None

        self.button_language_action.setVisible(False)

        def is_alive():
            return self.tab_is_alive

        # create logs info widget
        context = ProgramInfoContext(self.session, self.script_manager, self.executable_versions, self.program)

        self.widget_logs = ProgramInfoLogs(context, self.update_ui_state, self.set_widget_enabled, is_alive, self.show_download_wizard, self.set_program_callbacks_enabled)
        self.layout_logs.addWidget(self.widget_logs)

        # create files info widget
        context = ProgramInfoContext(self.session, self.script_manager, self.executable_versions, self.program)

        self.widget_files = ProgramInfoFiles(context, self.update_ui_state, self.set_widget_enabled, is_alive, self.show_upload_files_wizard, self.show_download_wizard)
        self.layout_files.addWidget(self.widget_files)

        self.update_ui_state()

    # override QWidget.showEvent
    def showEvent(self, event):
        if self.first_show_event:
            QTimer.singleShot(1, self.widget_logs.refresh_logs)
            QTimer.singleShot(1, self.widget_files.refresh_files)

            self.first_show_event = False

        self.set_program_callbacks_enabled(True)

        QWidget.showEvent(self, event)

    # override QWidget.hideEvent
    def hideEvent(self, event):
        self.set_program_callbacks_enabled(False)

        QWidget.hideEvent(self, event)

    def scheduler_state_changed(self, program):
        self.update_ui_state()

    def lite_scheduler_state_changed(self, program):
        self.status_changed.emit(self.program)

    def process_spawned(self, program):
        self.program.last_spawned_process.state_changed_callback = self.process_state_changed

        self.update_ui_state()

    def lite_process_spawned(self, program):
        self.program.last_spawned_lite_process.state_changed_callback = self.lite_process_state_changed

        self.status_changed.emit(self.program)

    def process_state_changed(self, process):
        self.update_ui_state()

    def lite_process_state_changed(self, process):
        self.status_changed.emit(self.program)

    def close_all_dialogs(self):
        self.tab_is_alive = False

        if self.edit_general_wizard != None:
            self.edit_general_wizard.close()

        if self.edit_language_wizard != None:
            self.edit_language_wizard.close()

        if self.edit_arguments_wizard != None:
            self.edit_arguments_wizard.close()

        if self.edit_stdio_wizard != None:
            self.edit_stdio_wizard.close()

        if self.edit_schedule_wizard != None:
            self.edit_schedule_wizard.close()

        if self.upload_files_wizard != None:
            self.upload_files_wizard.close()

        if self.download_wizard != None:
            self.download_wizard.close()

        if self.widget_language != None:
            self.widget_language.close_all_dialogs()

        self.widget_logs.close_all_dialogs()
        self.widget_files.close_all_dialogs()

    def set_program_callbacks_enabled(self, enable):
        self.program.enable_callbacks = enable

        if enable:
            self.refresh_program()

    def refresh_info(self):
        self.refresh_program()
        self.widget_logs.refresh_logs()
        self.widget_files.refresh_files()

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

    def update_ui_state(self):
        any_refresh_in_progress = self.program_refresh_in_progress or \
                                  self.widget_logs.refresh_in_progress or \
                                  self.widget_files.refresh_in_progress

        if any_refresh_in_progress:
            self.progress.setVisible(True)
            self.button_refresh.setText('Refreshing...')
            self.set_edit_buttons_enabled(False)
        else:
            self.progress.setVisible(False)
            self.button_refresh.setText('Refresh')
            self.set_edit_buttons_enabled(True)

        # general
        name              = self.program.cast_custom_option_value('name', str, '<unknown>')
        language_api_name = self.program.cast_custom_option_value('language', str, '<unknown>')
        description       = self.program.cast_custom_option_value('description', str, '')
        first_upload      = self.program.cast_custom_option_value('first_upload', int, 0)
        last_edit         = self.program.cast_custom_option_value('last_edit', int, 0)

        try:
            language_display_name = Constants.get_language_display_name(language_api_name)
        except:
            language_display_name = '<unknown>'

        self.label_name.setText(name)
        self.label_identifier.setText(self.program.identifier)
        self.label_language.setText(language_display_name)
        self.label_description.setText(description)
        self.label_first_upload.setText(timestamp_to_date_at_time(first_upload))
        self.label_last_edit.setText(timestamp_to_date_at_time(last_edit))

        start_mode_web_interface = has_program_start_mode_web_interface(self.program)

        # status
        self.group_status.setVisible(not start_mode_web_interface)

        process_running = False

        if self.program.last_spawned_process != None:
            date_at_time = timestamp_to_date_at_time(self.program.last_spawned_process.timestamp)

            if self.program.last_spawned_process.state == REDProcess.STATE_UNKNOWN:
                self.label_program_current_state.setText('Unknown since {0}'.format(date_at_time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_RUNNING:
                self.label_program_current_state.setText('Running since {0}'.format(date_at_time))
                process_running = True
            elif self.program.last_spawned_process.state == REDProcess.STATE_ERROR:
                if self.program.last_spawned_process.exit_code == REDProcess.E_INTERNAL_ERROR:
                    self.label_program_current_state.setText('Internal error occurred on {0}'.format(date_at_time))
                elif self.program.last_spawned_process.exit_code == REDProcess.E_CANNOT_EXECUTE:
                    self.label_program_current_state.setText('Could not be executed on {0}'.format(date_at_time))
                elif self.program.last_spawned_process.exit_code == REDProcess.E_DOES_NOT_EXIST:
                    self.label_program_current_state.setText('Executable does not exist on {0}'.format(date_at_time))
                else:
                    self.label_program_current_state.setText('Unknown error occurred on {0}'.format(date_at_time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_EXITED:
                if self.program.last_spawned_process.exit_code == 0:
                    self.label_program_current_state.setText('Not running, last run exited normally on {0}'.format(date_at_time))
                else:
                    self.label_program_current_state.setText('Not running, last run exited with an error (exit code: {0}) on {1}'
                                                            .format(self.program.last_spawned_process.exit_code, date_at_time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_KILLED:
                self.label_program_current_state.setText('Not running, last run was killed (signal: {0}) on {1}'
                                                         .format(self.program.last_spawned_process.exit_code, date_at_time))
            elif self.program.last_spawned_process.state == REDProcess.STATE_STOPPED:
                self.label_program_current_state.setText('Suspended on {0}'.format(date_at_time)) # FIXME: show resume button?

            self.label_last_program_start.setText(timestamp_to_date_at_time(self.program.last_spawned_timestamp))
        else:
            self.label_program_current_state.setText('Not running')
            self.label_last_program_start.setText('Never started')

        scheduler_stopped            = self.program.scheduler_state == REDProgram.SCHEDULER_STATE_STOPPED
        scheduler_state_display_name = Constants.api_scheduler_state_display_name.get(self.program.scheduler_state, '<unknown>')

        if scheduler_stopped:
            scheduler_state_display_name += ', no automatic program start'

        self.label_current_scheduler_state.setText(scheduler_state_display_name)
        self.label_last_scheduler_state_change.setText(timestamp_to_date_at_time(self.program.scheduler_timestamp))

        if self.program.scheduler_message != None:
            self.label_last_scheduler_message.setText(self.program.scheduler_message)
        else:
            self.label_last_scheduler_message.setText('None')

        self.set_widget_enabled(self.button_start_program, not any_refresh_in_progress and not process_running)
        self.set_widget_enabled(self.button_exit_process, not any_refresh_in_progress and process_running)
        self.set_widget_enabled(self.button_kill_process, not any_refresh_in_progress and process_running)
        self.set_widget_enabled(self.button_continue_schedule, not any_refresh_in_progress and scheduler_stopped and self.program.start_mode != REDProgram.START_MODE_NEVER)

        # logs
        self.group_logs.setVisible(not start_mode_web_interface)

        self.widget_logs.any_refresh_in_progress = any_refresh_in_progress
        self.widget_logs.update_ui_state()

        # files
        self.widget_files.any_refresh_in_progress = any_refresh_in_progress
        self.widget_files.update_ui_state()

        # language
        self.group_language.setTitle('{0} Configuration'.format(language_display_name))

        if self.widget_language != None:
            self.widget_language.update_ui_state()

            language_action, language_action_name = self.widget_language.get_language_action()

            if language_action != self.current_language_action:
                if self.current_language_action != None:
                    self.button_language_action.setVisible(False)
                    self.button_language_action.clicked.disconnect(self.current_language_action)

                if language_action != None:
                    self.button_language_action.clicked.connect(language_action)
                    self.button_language_action.setText(language_action_name)
                    self.button_language_action.setVisible(True)

                self.current_language_action = language_action

        # arguments
        self.group_arguments.setVisible(not start_mode_web_interface)

        arguments = []
        editable_arguments_offset = max(self.program.cast_custom_option_value('editable_arguments_offset', int, 0), 0)

        for argument in self.program.arguments.items[editable_arguments_offset:]:
            arguments.append(argument)

        self.label_arguments.setText('\n'.join(arguments))

        environment = []
        editable_environment_offset = max(self.program.cast_custom_option_value('editable_environment_offset', int, 0), 0)

        for variable in self.program.environment.items[editable_environment_offset:]:
            environment.append(variable)

        show_environment = self.check_show_environment.isChecked()

        self.label_environment_title.setVisible(show_environment)
        self.label_environment.setVisible(show_environment)
        self.label_environment.setText('\n'.join(environment))

        # stdio
        self.group_stdio.setVisible(not start_mode_web_interface)

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

        self.set_widget_enabled(self.edit_stdin_pipe_input, not any_refresh_in_progress and process_running)
        self.set_widget_enabled(self.button_send_stdin_pipe_input, not any_refresh_in_progress and process_running)

        if stdin_redirection_file:
            self.label_stdin_file.setText(self.program.stdin_file_name)

        self.label_stdout_target.setText(Constants.api_stdout_redirection_display_names.get(self.program.stdout_redirection, '<unknown>'))
        self.label_stdout_file_title.setVisible(stdout_redirection_file)
        self.label_stdout_file.setVisible(stdout_redirection_file)

        if stdout_redirection_file:
            self.label_stdout_file.setText(self.program.stdout_file_name)

        self.label_stderr_target.setText(Constants.api_stderr_redirection_display_names.get(self.program.stderr_redirection, '<unknown>'))
        self.label_stderr_file_title.setVisible(stderr_redirection_file)
        self.label_stderr_file.setVisible(stderr_redirection_file)

        if stderr_redirection_file:
            self.label_stderr_file.setText(self.program.stderr_file_name)

        # schedule
        self.group_schedule.setVisible(not start_mode_web_interface)

        start_mode_never    = self.program.start_mode == REDProgram.START_MODE_NEVER
        start_mode_always   = self.program.start_mode == REDProgram.START_MODE_ALWAYS
        start_mode_interval = self.program.start_mode == REDProgram.START_MODE_INTERVAL
        start_mode_cron     = self.program.start_mode == REDProgram.START_MODE_CRON

        start_mode_display_names  = Constants.api_start_mode_display_names.get(self.program.start_mode, '<unknown>')
        started_once_after_upload = self.program.cast_custom_option_value('started_once_after_upload', bool, False)

        if started_once_after_upload:
            start_mode_display_names += ' (was started once after upload)'

        self.label_start_mode.setText(start_mode_display_names)
        self.label_start_interval_title.setVisible(start_mode_interval)
        self.label_start_interval.setVisible(start_mode_interval)
        self.label_start_interval.setText('{0} seconds'.format(self.program.start_interval))
        self.label_start_fields_title.setVisible(start_mode_cron)
        self.label_start_fields.setVisible(start_mode_cron)

        if start_mode_cron:
            self.label_start_fields.setText(self.program.start_fields)

        self.label_continue_after_error_title.setVisible(not start_mode_never)
        self.label_continue_after_error.setVisible(not start_mode_never)

        if self.program.continue_after_error:
            self.label_continue_after_error.setText('Enabled')
        else:
            self.label_continue_after_error.setText('Disabled')

    def start_program(self):
        try:
            self.program.start()
        except (Error, REDError) as e:
            QMessageBox.critical(get_main_window(), 'Start Error',
                                 'Could not start program [{0}]:\n\n{1}'
                                 .format(self.program.cast_custom_option_value('name', str, '<unknown>'), e))

    def exit_process(self):
        if self.program.last_spawned_process != None:
            try:
                self.program.last_spawned_process.kill(REDProcess.SIGNAL_TERMINATE)
            except (Error, REDError) as e:
                QMessageBox.critical(get_main_window(), 'Exit Error',
                                     'Could not exit current process of program [{0}]:\n\n{1}'
                                     .format(self.program.cast_custom_option_value('name', str, '<unknown>'), e))
    def kill_process(self):
        if self.program.last_spawned_process != None:
            try:
                self.program.last_spawned_process.kill(REDProcess.SIGNAL_KILL)
            except (Error, REDError) as e:
                QMessageBox.critical(get_main_window(), 'Kill Error',
                                     'Could not kill current process of program [{0}]:\n\n{1}'
                                     .format(self.program.cast_custom_option_value('name', str, '<unknown>'), e))

    def continue_schedule(self):
        try:
            self.program.continue_schedule()
        except (Error, REDError) as e:
            QMessageBox.critical(get_main_window(), 'Schedule Error',
                                 'Could not continue schedule of program [{0}]:\n\n{1}'
                                 .format(self.program.cast_custom_option_value('name', str, '<unknown>'), e))

    def send_stdin_pipe_input(self):
        if self.program.last_spawned_process != None and self.program.last_spawned_process.stdin != None:
            try:
                self.program.last_spawned_process.stdin.write_async((self.edit_stdin_pipe_input.text() + '\n').encode('utf-8'))
            except (Error, REDError) as e:
                QMessageBox.critical(get_main_window(), 'Pipe Input Error',
                                     'Could not write to stdin of current process of program [{0}]:\n\n{1}'
                                     .format(self.program.cast_custom_option_value('name', str, '<unknown>'), e))
            else:
                self.edit_stdin_pipe_input.setText('')

    def set_widget_enabled(self, widget, enabled):
        # store current scroll position
        position = self.scroll_area.verticalScrollBar().value()

        widget.setEnabled(enabled)
        widget.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)

        # restore current scroll position, because en/disabling buttons
        # makes the scroll position jump for some reason
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

        self.button_refresh.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.button_edit_general.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.button_edit_language.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.button_edit_arguments.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.button_edit_stdio.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)
        self.button_edit_schedule.setAttribute(Qt.WA_TransparentForMouseEvents, not enabled)

        # restore current scroll position, because en/disabling buttons
        # makes the scroll position jump for some reason
        self.scroll_area.verticalScrollBar().setValue(position)

    def show_edit_general_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)
        page    = ProgramPageGeneral()

        self.edit_general_wizard = ProgramWizardEdit(self, context, self.program, self.widget_files.available_files, self.widget_files.available_directories)
        self.edit_general_wizard.setPage(Constants.PAGE_GENERAL, page)

        if self.edit_general_wizard.exec_() == QDialog.Accepted:
            page.apply_program_changes()
            self.refresh_info()
            self.name_changed.emit(self.program)

        self.edit_general_wizard = None

        if self.tab_is_alive:
            self.set_edit_buttons_enabled(True)

    def show_edit_language_wizard(self):
        language_api_name = self.program.cast_custom_option_value('language', str, '<unknown>')

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

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)
        page    = language_page_classes[language_page]()

        self.edit_language_wizard = ProgramWizardEdit(self, context, self.program, self.widget_files.available_files, self.widget_files.available_directories,)
        self.edit_language_wizard.setPage(language_page, page)

        if self.edit_language_wizard.exec_() == QDialog.Accepted:
            page.apply_program_changes()
            self.refresh_info()

        self.edit_language_wizard = None

        if self.tab_is_alive:
            self.set_edit_buttons_enabled(True)

    def show_edit_arguments_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)
        page    = ProgramPageArguments()

        self.edit_arguments_wizard = ProgramWizardEdit(self, context, self.program, self.widget_files.available_files, self.widget_files.available_directories)
        self.edit_arguments_wizard.setPage(Constants.PAGE_ARGUMENTS, page)

        if self.edit_arguments_wizard.exec_() == QDialog.Accepted:
            page.apply_program_changes()
            self.refresh_info()

        self.edit_arguments_wizard = None

        if self.tab_is_alive:
            self.set_edit_buttons_enabled(True)

    def show_edit_stdio_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)
        page    = ProgramPageStdio()

        self.edit_stdio_wizard = ProgramWizardEdit(self, context, self.program, self.widget_files.available_files, self.widget_files.available_directories)
        self.edit_stdio_wizard.setPage(Constants.PAGE_STDIO, page)

        if self.edit_stdio_wizard.exec_() == QDialog.Accepted:
            page.apply_program_changes()
            self.refresh_info()

        self.edit_stdio_wizard = None

        if self.tab_is_alive:
            self.set_edit_buttons_enabled(True)

    def show_edit_schedule_wizard(self):
        self.set_edit_buttons_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)
        page    = ProgramPageSchedule()

        self.edit_schedule_wizard = ProgramWizardEdit(self, context, self.program, self.widget_files.available_files, self.widget_files.available_directories)
        self.edit_schedule_wizard.setPage(Constants.PAGE_SCHEDULE, page)

        if self.edit_schedule_wizard.exec_() == QDialog.Accepted:
            page.apply_program_changes()
            self.refresh_info()

        self.edit_schedule_wizard = None

        if self.tab_is_alive:
            self.set_edit_buttons_enabled(True)

    def show_upload_files_wizard(self):
        self.set_edit_buttons_enabled(False)
        self.set_program_callbacks_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)

        self.upload_files_wizard = ProgramWizardUpload(self, context, self.program, self.last_upload_files_wizard_directory)
        self.upload_files_wizard.exec_()

        self.last_upload_files_wizard_directory = self.upload_files_wizard.last_directory

        if self.upload_files_wizard.upload_successful:
            self.widget_files.refresh_files()

        self.upload_files_wizard = None

        if self.tab_is_alive:
            self.set_program_callbacks_enabled(True)
            self.set_edit_buttons_enabled(True)

    def show_download_wizard(self, download_kind, download_directory, downloads):
        self.set_edit_buttons_enabled(False)
        self.set_program_callbacks_enabled(False)

        context = ProgramWizardContext(self.session, [], self.script_manager, self.image_version, self.executable_versions)

        self.download_wizard = ProgramWizardDownload(self, context, self.program, download_kind, download_directory, downloads)
        self.download_wizard.exec_()
        self.download_wizard = None

        if self.tab_is_alive:
            self.set_program_callbacks_enabled(True)
            self.set_edit_buttons_enabled(True)
