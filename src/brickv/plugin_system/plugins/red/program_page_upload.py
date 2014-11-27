# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_upload.py: Program Wizard Upload Page

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QWizard, QApplication, QPixmap
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_upload import Ui_ProgramPageUpload
from brickv.utils import get_program_path
import os
import posixpath
import stat
import time

class ProgramPageUpload(ProgramPage, Ui_ProgramPageUpload):
    CONFLICT_RESOLUTION_REPLACE = 1
    CONFLICT_RESOLUTION_RENAME  = 2
    CONFLICT_RESOLUTION_SKIP    = 3

    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.edit_mode                       = False
        self.conflict_resolution_in_progress = False
        self.auto_conflict_resolution        = None
        self.upload_successful               = False
        self.language_api_name               = None
        self.program                         = None
        self.root_directory                  = None
        self.remaining_uploads               = None
        self.upload                          = None
        self.command                         = None
        self.created_directories             = set()
        self.target_file                     = None
        self.source_file                     = None
        self.target_path                     = None
        self.source_path                     = None
        self.source_stat                     = None
        self.source_display_size             = None
        self.last_upload_size                = None
        self.replace_help_template           = unicode(self.label_replace_help.text())

        self.setTitle(title_prefix + 'Upload')

        self.progress_file.setVisible(False)

        self.check_rename_new_file.stateChanged.connect(self.update_ui_state)
        self.edit_new_name.textChanged.connect(self.check_new_name)
        self.button_reset_new_name.clicked.connect(self.reset_new_name)
        self.button_replace.clicked.connect(self.resolve_conflict_by_replace)
        self.button_rename.clicked.connect(self.resolve_conflict_by_rename)
        self.button_skip.clicked.connect(self.skip_conflict)
        self.button_start_upload.clicked.connect(self.start_upload)

        self.label_replace_icon.clear()
        self.label_replace_icon.setPixmap(QPixmap(os.path.join(get_program_path(), 'dialog-warning.png')))

        self.edit_new_name_checker = MandatoryLineEditChecker(self, self.label_new_name, self.edit_new_name)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Upload the {language} program [{name}].')

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            self.edit_mode = True

            self.set_formatted_sub_title(u'Upload new files for the {language} program [{name}].')

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.upload_successful and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        rename_new_file = self.check_rename_new_file.checkState() == Qt.Checked

        self.line1.setVisible(self.conflict_resolution_in_progress)
        self.label_replace_icon.setVisible(self.conflict_resolution_in_progress)
        self.label_replace_help.setVisible(self.conflict_resolution_in_progress)
        self.label_existing_file.setVisible(self.conflict_resolution_in_progress)
        self.label_existing_stats.setVisible(self.conflict_resolution_in_progress)
        self.label_new_file.setVisible(self.conflict_resolution_in_progress)
        self.label_new_stats.setVisible(self.conflict_resolution_in_progress)
        self.check_rename_new_file.setVisible(self.conflict_resolution_in_progress)
        self.label_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.edit_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.button_reset_new_name.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.label_new_name_help.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.check_remember_decision.setVisible(self.conflict_resolution_in_progress)
        self.button_replace.setVisible(self.conflict_resolution_in_progress and not rename_new_file)
        self.button_rename.setVisible(self.conflict_resolution_in_progress and rename_new_file)
        self.button_skip.setVisible(self.conflict_resolution_in_progress)
        self.line2.setVisible(self.conflict_resolution_in_progress)

    def check_new_name(self, name):
        name = unicode(name) # convert QString to unicode

        if len(name) == 0:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(False)
        elif name == posixpath.split(self.upload.target)[1] or \
             name == '.' or name == '..' or '/' in name:
            self.edit_new_name.setStyleSheet('QLineEdit { color : red }')
            self.button_rename.setEnabled(False)
        else:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(True)

    def reset_new_name(self):
        self.edit_new_name.setText(posixpath.split(self.upload.target)[1])

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit_log.appendHtml('<b>{0}</b>'.format(Qt.escape(message)))
        elif pre:
            self.edit_log.appendHtml('<pre>{0}</pre>'.format(message))
        else:
            self.edit_log.appendPlainText(message)

        self.edit_log.verticalScrollBar().setValue(self.edit_log.verticalScrollBar().maximum())

    def next_step(self, message, increase=1, log=True):
        self.progress_total.setValue(self.progress_total.value() + increase)
        self.label_current_step.setText(message)

        if log:
            self.log(message)

    def upload_error(self, message, defined=True):
        self.log(message, bold=True)

        if defined:
            pass # FIXME: purge program?

    def get_total_step_count(self):
        count = 0

        if not self.edit_mode:
            count += 1 # define new program
            count += 1 # set custom options

        count += 1 # upload files
        count += len(self.remaining_uploads)

        if not self.edit_mode and self.command != None:
            count += 1 # set command
            count += 1 # set more custom options

        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_STDIO):
            count += 1 # set stdio redirection

        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_SCHEDULE):
            count += 1 # set schedule

            if self.get_field('start_mode').toInt()[0] == Constants.START_MODE_ONCE:
                count += 1 # start once after upload

        count += 1 # upload successful

        return count

    def start_upload(self):
        self.button_start_upload.setEnabled(False)
        self.wizard().setOption(QWizard.DisabledBackButtonOnLastPage, True)

        self.remaining_uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

        if not self.edit_mode:
            self.language_api_name = Constants.language_api_names[self.get_field('language').toInt()[0]]
            self.command           = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_command()

        self.progress_total.setRange(0, self.get_total_step_count())

        # define new program
        if not self.edit_mode:
            self.next_step('Defining new program...', increase=0)

            identifier = str(self.get_field('identifier').toString())

            try:
                self.program = REDProgram(self.wizard().session).define(identifier) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e), False)
                return

            self.log('...done')

        # set custom options
        if not self.edit_mode:
            self.next_step('Setting custom options...')

            # set custom option: name
            name = unicode(self.get_field('name').toString())

            try:
                self.program.set_custom_option_value('name', name) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set custom option: language
            try:
                self.program.set_custom_option_value('language', self.language_api_name) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set custom option: description
            description = unicode(self.get_field('description').toString())

            try:
                self.program.set_custom_option_value('description', description) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set custom option: first_upload
            timestamp = int(time.time())

            try:
                self.program.set_custom_option_value('first_upload', timestamp) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set custom option: last_edit
            try:
                self.program.set_custom_option_value('last_edit', timestamp) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set language specific custom options
            custom_options = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_custom_options()

            for name, value in custom_options.iteritems():
                try:
                    self.program.set_custom_option_value(name, value) # FIXME: async_call
                except REDError as e:
                    self.upload_error(u'...error: {0}'.format(e))
                    return

            self.log('...done')

        # upload files
        self.next_step('Uploading files...', log=False)

        if self.edit_mode:
            self.root_directory = unicode(self.wizard().program.root_directory)
        else:
            self.root_directory = unicode(self.program.root_directory)

        self.progress_file.setRange(0, len(self.remaining_uploads))

        self.upload_next_file() # FIXME: abort upload once self.wizard().canceled is True

    def upload_next_file(self):
        if len(self.remaining_uploads) == 0:
            self.upload_files_done()
            return

        self.upload            = self.remaining_uploads[0]
        self.remaining_uploads = self.remaining_uploads[1:]
        self.source_path       = self.upload.source

        self.next_step(u'Uploading {0}...'.format(self.source_path))

        try:
            self.source_stat = os.stat(self.source_path)
            self.source_file = open(self.source_path, 'rb')
        except Exception as e:
            self.upload_error(u'...error opening source file {0}: {1}'.format(self.source_path, e))
            return

        self.source_display_size = get_file_display_size(self.source_stat.st_size)

        self.progress_file.setVisible(True)
        self.progress_file.setRange(0, self.source_stat.st_size)
        self.progress_file.setFormat(get_file_display_size(0) + ' of ' + self.source_display_size)
        self.progress_file.setValue(0)

        self.target_path = posixpath.join(self.root_directory, 'bin', self.upload.target)

        if len(posixpath.split(self.upload.target)[0]) > 0:
            target_directory = posixpath.split(self.target_path)[0]

            if target_directory not in self.created_directories:
                try:
                    create_directory(self.wizard().session, target_directory, DIRECTORY_FLAG_RECURSIVE, 0755, 1000, 1000)
                except REDError as e:
                    self.upload_error(u'...error creating target directory {0}: {1}'.format(target_directory, e))
                    return

                self.created_directories.add(target_directory)

        self.continue_upload_file()

    def continue_upload_file(self, replace_existing=False):
        self.progress_file.setVisible(True)

        flags = REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_EXCLUSIVE

        if replace_existing:
            flags |= REDFile.FLAG_REPLACE

        if (self.source_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)) != 0:
            permissions = 0755
        else:
            permissions = 0644

        try:
            self.target_file = REDFile(self.wizard().session).open(self.target_path, flags,
                                                                   permissions, 1000, 1000) # FIXME: async_call
        except REDError as e:
            if e.error_code == REDError.E_ALREADY_EXISTS:
                self.start_conflict_resolution()
            else:
                self.upload_error(u'...error opening target file {0}: {1}'.format(self.target_path, e))

            return

        self.upload_write_async()

    def start_conflict_resolution(self):
        self.log(u'...target file {0} already exists'.format(self.upload.target))

        if self.auto_conflict_resolution == ProgramPageUpload.CONFLICT_RESOLUTION_REPLACE:
            self.log(u'...replacing {0}'.format(self.upload.target))
            self.continue_upload_file(True)
        elif self.auto_conflict_resolution == ProgramPageUpload.CONFLICT_RESOLUTION_SKIP:
            self.log('...skipped')
            self.upload_next_file()
        else:
            self.progress_file.setVisible(False)

            target_parts = list(posixpath.split(self.upload.target))

            if len(target_parts[0]) == 0:
                target_parts[0] = '.'

            try:
                target_file = REDFile(self.wizard().session).open(self.target_path, REDFile.FLAG_READ_ONLY, 0, 1000, 1000) # FIXME: async_call

                self.label_existing_stats.setText('{0}, last modified on {1}'
                                                  .format(get_file_display_size(target_file.length),
                                                          timestamp_to_date_at_time(int(target_file.modification_time))))

                target_file.release()
            except REDError as e:
                self.label_existing_stats.setText(u'<b>Error</b>: Could not open target file: {0}', Qt.escape(unicode(e)))

            self.label_new_stats.setText('{0}, last modified on {1}'
                                         .format(self.source_display_size,
                                                 timestamp_to_date_at_time(int(self.source_stat.st_mtime))))

            self.label_replace_help.setText(self.replace_help_template.replace('<FILE>', self.upload.target))

            if self.auto_conflict_resolution == ProgramPageUpload.CONFLICT_RESOLUTION_RENAME:
                self.check_rename_new_file.setCheckState(Qt.Checked)
            else:
                self.check_rename_new_file.setCheckState(Qt.Unchecked)

            self.edit_new_name.setText('') # force a new-name check
            self.edit_new_name.setText(target_parts[1])

            self.conflict_resolution_in_progress = True
            self.update_ui_state()

    def resolve_conflict_by_replace(self):
        if not self.conflict_resolution_in_progress or self.check_rename_new_file.checkState() != Qt.Unchecked:
            return

        self.log(u'...replacing {0}'.format(self.upload.target))

        if self.check_remember_decision.checkState() == Qt.Checked:
            self.auto_conflict_resolution = ProgramPageUpload.CONFLICT_RESOLUTION_REPLACE
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.continue_upload_file(True)

    def rename_upload_target(self, new_name):
        if not self.conflict_resolution_in_progress:
            return

        self.upload      = Upload(self.upload.source, posixpath.join(posixpath.split(self.upload.target)[0], new_name))
        self.target_path = posixpath.join(self.root_directory, 'bin', self.upload.target)

    def resolve_conflict_by_rename(self):
        if not self.conflict_resolution_in_progress or self.check_rename_new_file.checkState() != Qt.Checked:
            return

        self.rename_upload_target(unicode(self.edit_new_name.text()))
        self.log(u'...uploading as {0}'.format(self.upload.target))

        if self.check_remember_decision.checkState() == Qt.Checked:
            self.auto_conflict_resolution = ProgramPageUpload.CONFLICT_RESOLUTION_RENAME
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.continue_upload_file(False)

    def skip_conflict(self):
        if not self.conflict_resolution_in_progress:
            return

        if self.check_remember_decision.checkState() == Qt.Checked:
            self.auto_conflict_resolution = ProgramPageUpload.CONFLICT_RESOLUTION_SKIP
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.log('...skipped')
        self.upload_next_file()

    def upload_write_async_cb_status(self, upload_size, upload_total):
        uploaded = self.progress_file.value() + upload_size - self.last_upload_size
        self.progress_file.setValue(uploaded)
        self.progress_file.setFormat(get_file_display_size(uploaded) + ' of ' + self.source_display_size)
        self.last_upload_size = upload_size

    def upload_write_async_cb_result(self, error):
        if error == None:
            self.upload_write_async()
        else:
            self.upload_error(u'...error writing target file {0}: {1}'.format(self.target_path, error))

    def upload_write_async(self):
        try:
            data = self.source_file.read(1000*1000*10) # Read 10mb at a time
        except Exception as e:
            self.upload_error(u'...error reading source file {0}: {1}'.format(self.source_path, e))
            return

        if len(data) == 0:
            self.upload_write_async_done()
            return

        self.last_upload_size = 0

        try:
            self.target_file.write_async(data, self.upload_write_async_cb_error, self.upload_write_async_cb_status)
        except REDError as e:
            self.upload_error(u'...error writing target file {0}: {1}'.format(self.target_path, e))

    def upload_write_async_done(self):
        self.log('...done')
        self.progress_file.setValue(self.progress_file.maximum())

        self.target_file.release()
        self.source_file.close()

        self.upload_next_file()

    def upload_files_done(self):
        self.progress_file.setVisible(False)

        # FIXME: move compile steps after setting mode of the config, so the
        # program doesn't end up in an half condfigured state if compilation fails
        if self.language_api_name == 'c':
            if self.get_field('c.compile_from_source').toBool():
                self.compile_make()
                return
        elif self.language_api_name == 'delphi':
            if self.get_field('delphi.compile_from_source').toBool():
                self.compile_fpcmake()
                return

        self.set_configuration()

    def set_configuration(self):
        # set command
        if not self.edit_mode and self.command != None:
            self.next_step('Setting command...')

            executable, arguments, environment, working_directory = self.command

            editable_arguments_offset   = len(arguments)
            editable_environment_offset = len(environment)

            if self.wizard().hasVisitedPage(Constants.PAGE_ARGUMENTS):
                arguments   += self.wizard().page(Constants.PAGE_ARGUMENTS).get_arguments()
                environment += self.wizard().page(Constants.PAGE_ARGUMENTS).get_environment()

            try:
                self.program.set_command(executable, arguments, environment, working_directory) # FIXME: async_call
            except REDError as e:
                self.upload_error('...error: {0}'.format(e))
                return

            self.log('...done')

            # set more custom options
            self.next_step('Setting more custom options...')

            # set custom option: editable_arguments_offset
            try:
                self.program.set_custom_option_value('editable_arguments_offset', str(editable_arguments_offset)) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            # set custom option: editable_environment_offset
            try:
                self.program.set_custom_option_value('editable_environment_offset', str(editable_environment_offset)) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            self.log('...done')

        # set stdio redirection
        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_STDIO):
            self.next_step('Setting stdio redirection...')

            stdin_redirection  = Constants.api_stdin_redirections[self.get_field('stdin_redirection').toInt()[0]]
            stdout_redirection = Constants.api_stdout_redirections[self.get_field('stdout_redirection').toInt()[0]]
            stderr_redirection = Constants.api_stderr_redirections[self.get_field('stderr_redirection').toInt()[0]]
            stdin_file         = unicode(self.get_field('stdin_file').toString())
            stdout_file        = unicode(self.get_field('stdout_file').toString())
            stderr_file        = unicode(self.get_field('stderr_file').toString())

            try:
                self.program.set_stdio_redirection(stdin_redirection, stdin_file,
                                                   stdout_redirection, stdout_file,
                                                   stderr_redirection, stderr_file) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            self.log('...done')

        # set schedule
        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_SCHEDULE):
            self.next_step('Setting schedule...')

            start_mode = self.get_field('start_mode').toInt()[0]

            if start_mode == Constants.START_MODE_ONCE:
                api_start_mode          = REDProgram.START_MODE_NEVER
                start_once_after_upload = True
            else:
                api_start_mode          = Constants.api_start_modes[start_mode]
                start_once_after_upload = False

            continue_after_error = self.get_field('continue_after_error').toBool()
            start_interval       = self.get_field('start_interval').toUInt()[0]
            start_fields         = unicode(self.get_field('start_fields').toString())

            try:
                self.program.set_schedule(api_start_mode, continue_after_error, start_interval, start_fields) # FIXME: async_call
            except REDError as e:
                self.upload_error(u'...error: {0}'.format(e))
                return

            self.log('...done')

            # start once after upload, if enabled
            if start_once_after_upload:
                self.next_step('Starting...')

                try:
                    self.program.set_custom_option_value('started_once_after_upload', True) # FIXME: async_call
                except REDError as e:
                    self.upload_error(u'...error: {0}'.format(e))
                    return

                try:
                    self.program.start() # FIXME: async_call
                except REDError as e:
                    self.upload_error(u'...error: {0}'.format(e))
                    return

                self.log('...done')

        # upload successful
        self.next_step('Upload successful!')

        self.progress_total.setValue(self.progress_total.maximum())

        self.wizard().setOption(QWizard.NoCancelButton, True)
        self.upload_successful = True
        self.completeChanged.emit()

    def compile_make(self):
        def cb_make_helper(result):
            if result != None:
                for s in result.stdout.rstrip().split('\n'):
                    self.log(s, pre=True)

                if result.exit_code != 0:
                    self.upload_error('...error')
                else:
                    self.log('...done')
                    self.set_configuration()
            else:
                self.upload_error('...error')

        self.next_step('Executing make...')

        make_options      = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_make_options()
        working_directory = posixpath.join(unicode(self.program.root_directory), 'bin', unicode(self.program.working_directory))

        self.wizard().script_manager.execute_script('make_helper', cb_make_helper, [working_directory] + make_options,
                                                    max_length=1024*1024, redirect_stderr_to_stdout=True)

    def compile_fpcmake(self):
        def cb_fpcmake_helper(result):
            if result != None:
                for s in result.stdout.rstrip().split('\n'):
                    self.log(s, pre=True)

                if result.exit_code != 0:
                    self.upload_error('...error')
                else:
                    self.log('...done')
                    self.set_configuration()
            else:
                self.upload_error('...error')

        self.next_step('Executing fpcmake and make...')

        make_options      = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_make_options()
        working_directory = posixpath.join(unicode(self.program.root_directory), 'bin', unicode(self.program.working_directory))

        self.wizard().script_manager.execute_script('fpcmake_helper', cb_fpcmake_helper, [working_directory] + make_options,
                                                    max_length=1024*1024, redirect_stderr_to_stdout=True)
