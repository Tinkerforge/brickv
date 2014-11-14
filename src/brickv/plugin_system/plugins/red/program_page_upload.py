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

from PyQt4.QtGui import QWizard, QApplication
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_upload import Ui_ProgramPageUpload
import os
import stat
import time

class ProgramPageUpload(ProgramPage, Ui_ProgramPageUpload):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        # state for async file upload
        self.upload_successful = False
        self.language_api_name = None
        self.program           = None
        self.root_directory    = None
        self.uploads           = None
        self.target            = None
        self.source            = None
        self.target_name       = None
        self.source_name       = None
        self.source_size       = None
        self.last_upload_size  = None

        self.setTitle(title_prefix + 'Upload')

        self.progress_file.setVisible(False)

        self.button_start_upload.clicked.connect(self.start_upload)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Upload the {language} program [{name}].')
        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.upload_successful and ProgramPage.isComplete(self)

    def update_ui_state(self):
        pass

    def log(self, message):
        self.list_log.addItem(message)
        self.list_log.scrollToBottom()

    def next_step(self, message, increase=1, log=True):
        self.progress_total.setValue(self.progress_total.value() + increase)
        self.label_current_step.setText(message)

        if log:
            self.log(message)

    def upload_error(self, message, defined=True):
        self.log(message)

        if defined:
            pass # FIXME: purge program?

    def start_upload(self):
        self.button_start_upload.setEnabled(False)
        self.wizard().setOption(QWizard.DisabledBackButtonOnLastPage, True)

        self.uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

        self.progress_total.setRange(0, 6 + len(self.uploads))

        # define new program
        identifier = str(self.get_field('identifier').toString())

        self.next_step('Defining new program...', increase=0)

        try:
            self.program = REDProgram(self.wizard().session).define(identifier) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e), False)
            return

        self.log('...done')

        # set custom options
        self.next_step('Setting custom options...')

        # set custom option: name
        name = unicode(self.get_field('name').toString())

        try:
            self.program.set_custom_option_value('name', name) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set custom option: language
        self.language_api_name = Constants.language_api_names[self.get_field('language').toInt()[0]]

        try:
            self.program.set_custom_option_value('language', self.language_api_name) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set custom option: description
        description = unicode(self.get_field('description').toString())

        try:
            self.program.set_custom_option_value('description', description) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set custom option: first_upload
        timestamp = int(time.time())

        try:
            self.program.set_custom_option_value('first_upload', timestamp) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set custom option: last_edit
        try:
            self.program.set_custom_option_value('last_edit', timestamp) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set language specific custom options
        custom_options = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_custom_options()

        for name, value in custom_options.iteritems():
            try:
                self.program.set_custom_option_value(name, value) # FIXME: async_call
            except REDError as e:
                self.upload_error('...error: {0}'.format(e))
                return

        self.log('...done')

        # upload files
        self.next_step('Uploading files...', log=False)

        self.root_directory = unicode(self.program.root_directory)

        self.progress_file.setRange(0, len(self.uploads))

        self.upload_next_file() # FIXME: abort upload once self.wizard().canceled is True

    def upload_next_file(self):
        if len(self.uploads) == 0:
            self.upload_files_done()
            return

        upload = self.uploads[0]
        self.uploads = self.uploads[1:]

        self.source_name = upload.source

        self.next_step(u'Uploading {0}...'.format(self.source_name))

        self.progress_file.setVisible(True)
        self.progress_file.setRange(0, 0)
        self.progress_file.setValue(0)

        try:
            source_st = os.stat(self.source_name)
            self.source = open(self.source_name, 'rb')
        except Exception as e:
            self.upload_error(u"...error opening source file '{0}': {1}".format(self.source_name, e))
            return

        self.source_size = source_st.st_size
        self.progress_file.setRange(0, self.source_size)

        self.target_name = os.path.join(self.root_directory, 'bin', upload.target)

        if len(os.path.split(upload.target)[0]) > 0:
            target_directory = os.path.split(self.target_name)[0]

            try:
                create_directory(self.wizard().session, target_directory, DIRECTORY_FLAG_RECURSIVE, 0755, 1000, 1000)
            except REDError as e:
                self.upload_error("...error creating target directory '{0}': {1}".format(target_directory, e))
                return

        if (source_st.st_mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)) != 0:
            permissions = 0755
        else:
            permissions = 0644

        try:
            self.target = REDFile(self.wizard().session).open(self.target_name,
                                                              REDFile.FLAG_WRITE_ONLY |
                                                              REDFile.FLAG_CREATE |
                                                              REDFile.FLAG_NON_BLOCKING |
                                                              REDFile.FLAG_TRUNCATE,
                                                              permissions, 1000, 1000) # FIXME: async_call
        except REDError as e:
            self.upload_error(u"...error opening target file '{0}': {1}".format(self.target_name, e))
            return

        self.upload_write_async()

    def upload_write_async_cb_status(self, upload_size, upload_of):
        uploaded = self.progress_file.value() + upload_size - self.last_upload_size
        self.progress_file.setValue(uploaded)
        self.progress_file.setFormat('{0} kiB of {1} kiB'.format(uploaded/1024, self.source_size/1024))
        self.last_upload_size = upload_size

    def upload_write_async_cb_error(self, error):
        if error == None:
            self.upload_write_async()
        else:
            self.upload_error(u"...error writing target file '{0}': {1}".format(self.target_name, str(error)))

    def upload_write_async(self):
        try:
            data = self.source.read(1000*1000*10) # Read 10mb at a time
        except Exception as e:
            self.upload_error(u"...error reading source file '{0}': {1}".format(self.source_name, e))
            return

        if len(data) == 0:
            self.upload_write_async_done()
            return

        self.last_upload_size = 0

        try:
            self.target.write_async(data, self.upload_write_async_cb_error, self.upload_write_async_cb_status)
        except REDError as e:
            self.upload_error(u"...error writing target file '{0}': {1}".format(self.target_name, e))

    def upload_write_async_done(self):
        self.log('...done')
        self.progress_file.setValue(self.progress_file.maximum())

        self.target.release()
        self.source.close()

        self.upload_next_file()

    def upload_files_done(self):
        self.progress_file.setVisible(False)

        if self.language_api_name == 'c':
            if self.get_field('c.compile_from_source').toBool():
                self.compile_make()
                return
        elif self.language_api_name == 'delphi':
            start_mode = self.get_field('delphi.start_mode').toInt()[0]

            if start_mode == Constants.DELPHI_START_MODE_COMPILE:
                self.compile_fpc()
                return

        self.upload_configuration()

    def upload_configuration(self):
        # set command
        command = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_command()

        if command != None:
            self.next_step('Setting command...')

            executable, arguments, environment, working_directory = command

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
                self.upload_error('...error: {0}'.format(e))
                return

            # set custom option: editable_environment_offset
            try:
                self.program.set_custom_option_value('editable_environment_offset', str(editable_environment_offset)) # FIXME: async_call
            except REDError as e:
                self.upload_error('...error: {0}'.format(e))
                return

            self.log('...done')

        # set stdio redirection
        if self.wizard().hasVisitedPage(Constants.PAGE_STDIO):
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
                self.upload_error('...error: {0}'.format(e))
                return

            self.log('...done')

        # set schedule
        if self.wizard().hasVisitedPage(Constants.PAGE_SCHEDULE):
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
                self.upload_error('...error: {0}'.format(e))
                return

            self.log('...done')

            # start once after upload, if enabled
            if start_once_after_upload:
                self.next_step('Starting...')

                try:
                    self.program.set_custom_option_value('started_once_after_upload', 'yes') # FIXME: async_call
                except REDError as e:
                    self.upload_error('...error: {0}'.format(e))
                    return

                try:
                    self.program.start() # FIXME: async_call
                except REDError as e:
                    self.upload_error('...error: {0}'.format(e))
                    return

                self.log('...done')

        self.next_step('Upload successful!')

        self.progress_total.setValue(self.progress_total.maximum())

        self.wizard().setOption(QWizard.NoCancelButton, True)
        self.upload_successful = True
        self.completeChanged.emit()

    def compile_make(self):
        def cb(result):
            if result != None and result.stderr == '':
                for s in result.stdout.split('\n'):
                    self.log(s)
                self.log('...done')
                self.upload_configuration()
            else:
                if result != None:
                    for s in result.stderr.split('\n'):
                        self.log(s)
                self.log('...error')

        self.next_step('Calling make...')

        make_options      = self.wizard().page(Constants.get_language_page(self.language_api_name)).get_make_options()
        working_directory = os.path.join(unicode(self.program.root_directory), 'bin', unicode(self.program.working_directory))

        self.wizard().script_manager.execute_script('make_helper', cb, [working_directory] + make_options)

    def compile_fpc(self):
        def cb(result):
            if result != None and len(result.stderr.split('\n')) < 3:
                for s in result.stdout.split('\n'):
                    self.log(s)
                self.log('...done')
                self.upload_configuration()
            else:
                if result != None:
                    for s in result.stderr.split('\n'):
                        self.log(s)
                self.log('...error')

        self.next_step('Calling fpc...')

        compile_options   = unicode(self.get_field('delphi.compile_options').toString())
        main_source_file  = unicode(self.get_field('delphi.main_source_file').toString())
        working_directory = os.path.join(unicode(self.program.root_directory), 'bin', unicode(self.program.working_directory))

        self.wizard().script_manager.execute_script('fpc_helper', cb, [working_directory, '{0} {1}'.format(compile_options, main_source_file)])
