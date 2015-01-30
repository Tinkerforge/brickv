# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>
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
from PyQt4.QtGui import QWizard, QPixmap
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_upload import Ui_ProgramPageUpload
from brickv.utils import get_resources_path
import os
import posixpath
import stat
import time

class ChunkedUploader(ChunkedUploaderBase):
    def __init__(self, page):
        ChunkedUploaderBase.__init__(self, page.wizard().session)

        self.page = page

    def report_error(self, message, *args):
        self.page.upload_error(u'...error: ' + message, *args)

    def set_progress_maximum(self, maximum):
        self.page.progress_file.setRange(0, maximum)

    def set_progress_value(self, value, message):
        self.page.progress_file.setValue(value)
        self.page.progress_file.setFormat(message)

    def done(self):
        self.page.chunked_uploader = None

        self.page.log('...done')
        self.page.upload_next_file()

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
        self.target_path                     = None # abolsute path on RED Brick in POSIX format
        self.chunked_uploader                = None
        self.replace_help_template           = self.label_replace_help.text()
        self.warnings                        = 0
        self.canceled                        = False

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
        self.label_replace_icon.setPixmap(QPixmap(os.path.join(get_resources_path(), 'dialog-warning.png')))

        self.edit_new_name_checker = MandatoryLineEditChecker(self, self.label_new_name, self.edit_new_name)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Upload the {language} program [{name}].')

        self.wizard().rejected.connect(self.cancel_upload)

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
        rename_new_file = self.check_rename_new_file.isChecked()

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

    def cancel_upload(self):
        self.canceled    = True
        chunked_uploader = self.chunked_uploader

        if chunked_uploader != None:
            chunked_uploader.canceled = True

    def check_new_name(self, name):
        target = posixpath.split(self.upload.target)[1]

        if len(name) == 0:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(False)
        elif name == target or name == '.' or name == '..' or '/' in name:
            self.edit_new_name.setStyleSheet('QLineEdit { color : red }')
            self.button_rename.setEnabled(False)
        else:
            self.edit_new_name.setStyleSheet('')
            self.button_rename.setEnabled(True)

    def reset_new_name(self):
        self.edit_new_name.setText(posixpath.split(self.upload.target)[1])

    def log(self, message, bold=False, pre=False):
        if bold:
            self.edit_log.appendHtml(u'<b>{0}</b>'.format(Qt.escape(message)))
        elif pre:
            self.edit_log.appendHtml(u'<pre>{0}</pre>'.format(message))
        else:
            self.edit_log.appendPlainText(message)

        self.edit_log.verticalScrollBar().setValue(self.edit_log.verticalScrollBar().maximum())

    def next_step(self, message, increase=1, log=True):
        self.progress_total.setValue(self.progress_total.value() + increase)
        self.label_current_step.setText(message)

        if log:
            self.log(message)

    def upload_warning(self, message, *args, **kwargs):
        self.warnings += 1

        string_args = []

        for arg in args:
            string_args.append(Qt.escape(unicode(arg)))

        if len(string_args) > 0:
            message = unicode(message).format(*tuple(string_args))

        self.log(message, bold=True)

    def upload_error(self, message, *args, **kwargs):
        string_args = []

        for arg in args:
            string_args.append(Qt.escape(unicode(arg)))

        if len(string_args) > 0:
            message = unicode(message).format(*tuple(string_args))

        self.log(message, bold=True)

        if 'defined' in kwargs:
            defined = kwargs['defined']
        else:
            defined = True

        if not self.edit_mode and defined:
            try:
                self.program.purge() # FIXME: async_call
            except (Error, REDError):
                pass # FIXME: report this error?

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

            if self.get_field('start_mode') == Constants.START_MODE_ONCE:
                count += 1 # start once after upload

        count += 1 # upload successful

        return count

    def start_upload(self):
        self.button_start_upload.setEnabled(False)
        self.wizard().setOption(QWizard.DisabledBackButtonOnLastPage, True)

        self.remaining_uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

        if not self.edit_mode:
            self.language_api_name = Constants.language_api_names[self.get_field('language')]
            self.command           = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_command()

        self.progress_total.setRange(0, self.get_total_step_count())

        # define new program
        if not self.edit_mode:
            self.next_step('Defining new program...', increase=0)

            identifier = self.get_field('identifier')

            try:
                self.program = REDProgram(self.wizard().session).define(identifier) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e, defined=False)
                return

            self.log('...done')

        # set custom options
        if not self.edit_mode:
            self.next_step('Setting custom options...')

            # set custom option: name
            name = self.get_field('name')

            try:
                self.program.set_custom_option_value('name', name) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set custom option: language
            try:
                self.program.set_custom_option_value('language', self.language_api_name) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set custom option: description
            description = self.get_field('description')

            try:
                self.program.set_custom_option_value('description', description) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set custom option: first_upload
            timestamp = int(time.time())

            try:
                self.program.set_custom_option_value('first_upload', timestamp) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set custom option: last_edit
            try:
                self.program.set_custom_option_value('last_edit', timestamp) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set language specific custom options
            custom_options = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_custom_options()

            for name, value in custom_options.iteritems():
                try:
                    self.program.set_custom_option_value(name, value) # FIXME: async_call
                except (Error, REDError) as e:
                    self.upload_error('...error: {0}', e)
                    return

            self.log('...done')

        # upload files
        self.next_step('Uploading files...', log=False)

        if self.edit_mode:
            self.root_directory = self.wizard().program.root_directory
        else:
            self.root_directory = self.program.root_directory

        self.progress_file.setRange(0, len(self.remaining_uploads))

        self.upload_next_file()

    def upload_next_file(self):
        if self.canceled:
            return

        if len(self.remaining_uploads) == 0:
            self.progress_file.setVisible(False)
            self.set_configuration()
            return

        self.upload            = self.remaining_uploads[0]
        self.remaining_uploads = self.remaining_uploads[1:]
        source_path            = self.upload.source

        self.next_step(u'Uploading {0}...'.format(source_path))

        try:
            self.source_stat = os.stat(source_path)
            self.source_file = open(source_path, 'rb')
        except Exception as e:
            self.upload_error('...error: Could not open source file {0}: {1}', source_path, e)
            return

        self.chunked_uploader = ChunkedUploader(self)

        if not self.chunked_uploader.prepare(source_path):
            return

        self.target_path = posixpath.join(self.root_directory, 'bin', self.upload.target)

        # create target directory, if necessary
        if len(posixpath.split(self.upload.target)[0]) > 0:
            target_directory = posixpath.split(self.target_path)[0]

            if target_directory not in self.created_directories:
                try:
                    create_directory(self.wizard().session, target_directory, DIRECTORY_FLAG_RECURSIVE, 0o755, 1000, 1000)
                except (Error, REDError) as e:
                    self.upload_error('...error: Could not create target directory {0}: {1}', target_directory, e)
                    return

                self.created_directories.add(target_directory)

        self.continue_upload_file()

    def continue_upload_file(self, replace_existing=False):
        flags = REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_EXCLUSIVE

        if replace_existing:
            flags |= REDFile.FLAG_REPLACE

        # FIXME: preserving the executable bit this way only works well on
        #        Linux and Mac OS X hosts. on Windows Python deduces this from
        #        the file extension. this does not work if the executable is
        #        cross-compiled and doesn't have the typical Windows file
        #        extensions for executables
        if (self.source_stat.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)) != 0:
            permissions = 0o755
        else:
            permissions = 0o644

        # FIXME: workaround permission problem were this really matters (C/C++
        #        and Delphi/Lazarus with cross-compiled executables)
        if not self.edit_mode and \
           self.language_api_name in ['c', 'delphi'] and \
           posixpath.normpath(self.command[0]) == posixpath.normpath(self.upload.target):
            permissions = 0o755

        try:
            self.target_file = REDFile(self.wizard().session).open(self.target_path, flags,
                                                                   permissions, 1000, 1000) # FIXME: async_call
        except (Error, REDError) as e:
            if e.error_code == REDError.E_ALREADY_EXISTS:
                self.start_conflict_resolution()
            else:
                self.upload_error('...error: Could not open target file {0}: {1}', self.target_path, e)

            return

        self.progress_file.setVisible(True)
        self.chunked_uploader.start(self.target_path, self.target_file)

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

            try:
                target_file = REDFile(self.wizard().session).open(self.target_path, REDFile.FLAG_READ_ONLY, 0, 1000, 1000) # FIXME: async_call

                self.label_existing_stats.setText('{0}, last modified on {1}'
                                                  .format(get_file_display_size(target_file.length),
                                                          timestamp_to_date_at_time(int(target_file.modification_time))))

                target_file.release()
            except (Error, REDError) as e:
                self.label_existing_stats.setText(u'<b>Error</b>: Could not open target file: {0}', Qt.escape(unicode(e)))

            self.label_new_stats.setText('{0}, last modified on {1}'
                                         .format(self.chunked_uploader.source_display_size,
                                                 timestamp_to_date_at_time(int(self.chunked_uploader.source_stat.st_mtime))))

            self.label_replace_help.setText(self.replace_help_template.replace('<FILE>', Qt.escape(self.upload.target)))
            self.check_rename_new_file.setChecked(self.auto_conflict_resolution == ProgramPageUpload.CONFLICT_RESOLUTION_RENAME)
            self.edit_new_name.setText('') # force a new-name check
            self.edit_new_name.setText(posixpath.split(self.upload.target)[1])

            self.conflict_resolution_in_progress = True
            self.update_ui_state()

    def resolve_conflict_by_replace(self):
        if not self.conflict_resolution_in_progress or self.check_rename_new_file.isChecked():
            return

        self.log(u'...replacing {0}'.format(self.upload.target))

        if self.check_remember_decision.isChecked():
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
        if not self.conflict_resolution_in_progress or not self.check_rename_new_file.isChecked():
            return

        self.rename_upload_target(self.edit_new_name.text())
        self.log(u'...uploading as {0}'.format(self.upload.target))

        if self.check_remember_decision.isChecked():
            self.auto_conflict_resolution = ProgramPageUpload.CONFLICT_RESOLUTION_RENAME
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.continue_upload_file(False)

    def skip_conflict(self):
        if not self.conflict_resolution_in_progress:
            return

        if self.check_remember_decision.isChecked():
            self.auto_conflict_resolution = ProgramPageUpload.CONFLICT_RESOLUTION_SKIP
        else:
            self.auto_conflict_resolution = None

        self.conflict_resolution_in_progress = False
        self.update_ui_state()

        self.log('...skipped')
        self.upload_next_file()

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
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            self.log('...done')

            # set more custom options
            self.next_step('Setting more custom options...')

            # set custom option: editable_arguments_offset
            try:
                self.program.set_custom_option_value('editable_arguments_offset', str(editable_arguments_offset)) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            # set custom option: editable_environment_offset
            try:
                self.program.set_custom_option_value('editable_environment_offset', str(editable_environment_offset)) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            self.log('...done')

        # set stdio redirection
        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_STDIO):
            self.next_step('Setting stdio redirection...')

            stdin_redirection  = Constants.api_stdin_redirections[self.get_field('stdin_redirection')]
            stdout_redirection = Constants.api_stdout_redirections[self.get_field('stdout_redirection')]
            stderr_redirection = Constants.api_stderr_redirections[self.get_field('stderr_redirection')]
            stdin_file         = self.get_field('stdin_file')
            stdout_file        = self.get_field('stdout_file')
            stderr_file        = self.get_field('stderr_file')

            try:
                self.program.set_stdio_redirection(stdin_redirection, stdin_file,
                                                   stdout_redirection, stdout_file,
                                                   stderr_redirection, stderr_file) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            self.log('...done')

        if self.language_api_name == 'c' and self.get_field('c.compile_from_source'):
            self.compile_make()
            return
        elif self.language_api_name == 'delphi' and self.get_field('delphi.compile_from_source'):
            self.compile_fpcmake()
            return

        self.set_schedule()

    def set_schedule(self):
        # set schedule
        if not self.edit_mode and self.wizard().hasVisitedPage(Constants.PAGE_SCHEDULE):
            self.next_step('Setting schedule...')

            start_mode = self.get_field('start_mode')

            if start_mode == Constants.START_MODE_ONCE:
                api_start_mode          = REDProgram.START_MODE_NEVER
                start_once_after_upload = True
            else:
                api_start_mode          = Constants.api_start_modes[start_mode]
                start_once_after_upload = False

            continue_after_error = self.get_field('continue_after_error')
            start_interval       = self.get_field('start_interval')
            start_fields         = self.get_field('start_fields')

            try:
                self.program.set_schedule(api_start_mode, continue_after_error, start_interval, start_fields) # FIXME: async_call
            except (Error, REDError) as e:
                self.upload_error('...error: {0}', e)
                return

            self.log('...done')

            # start once after upload, if enabled
            if start_once_after_upload:
                self.next_step('Starting...')

                try:
                    self.program.set_custom_option_value('started_once_after_upload', True) # FIXME: async_call
                except (Error, REDError) as e:
                    self.upload_error('...error: {0}', e)
                    return

                try:
                    self.program.start() # FIXME: async_call
                except (Error, REDError) as e:
                    self.upload_error('...error: {0}', e)
                    return

                self.log('...done')

        self.upload_done()

    def upload_done(self):
        if self.warnings == 1:
            self.next_step('Upload finished with 1 warning!')
        elif self.warnings > 1:
            self.next_step('Upload finished with {0} warnings!'.format(self.warnings))
        else:
            self.next_step('Upload successful!')

        self.progress_total.setValue(self.progress_total.maximum())

        self.wizard().setOption(QWizard.NoCancelButton, True)
        self.upload_successful = True
        self.completeChanged.emit()

    def compile_make(self):
        def cb_make_helper(result):
            if result == None:
                self.upload_warning('...warning: Could not execute make helper script')
                self.upload_done()
                return

            if result.stdout == None:
                self.upload_warning('...warning: Output of make helper script is not UTF-8 encoded')
                self.upload_done()
                return

            for s in result.stdout.rstrip().split('\n'):
                self.log(s, pre=True)

            if result.exit_code != 0:
                self.upload_warning('...warning: Could not compile source code')
                self.upload_done()
            else:
                self.log('...done')
                self.set_schedule()

        self.next_step('Executing make...')

        make_options      = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_make_options()
        working_directory = posixpath.join(self.program.root_directory, 'bin', self.program.working_directory)

        self.wizard().script_manager.execute_script('make_helper', cb_make_helper, [working_directory] + make_options,
                                                    max_length=1024*1024, redirect_stderr_to_stdout=True,
                                                    execute_as_user=True)

    def compile_fpcmake(self):
        def cb_fpcmake_helper(result):
            if result == None:
                self.upload_warning('...warning: Could not execute fpcmake helper script')
                self.upload_done()
                return

            if result.stdout == None:
                self.upload_warning('...warning: Output of fpcmake helper script is not UTF-8 encoded')
                self.upload_done()
                return

            for s in result.stdout.rstrip().split('\n'):
                self.log(s, pre=True)

            if result.exit_code != 0:
                self.upload_warning('...warning: Could not compile source code')
                self.upload_done()
            else:
                self.log('...done')
                self.set_schedule()

        self.next_step('Executing fpcmake and make...')

        make_options      = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_make_options()
        working_directory = posixpath.join(self.program.root_directory, 'bin', self.program.working_directory)

        self.wizard().script_manager.execute_script('fpcmake_helper', cb_fpcmake_helper, [working_directory] + make_options,
                                                    max_length=1024*1024, redirect_stderr_to_stdout=True,
                                                    execute_as_user=True)
