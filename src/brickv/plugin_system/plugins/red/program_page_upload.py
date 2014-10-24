# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtGui import QWizard, QWizardPage
from brickv.plugin_system.plugins.red.api import REDError, REDFile, REDProgram
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_upload import Ui_ProgramPageUpload
import os

class ProgramPageUpload(QWizardPage, Ui_ProgramPageUpload):
    def __init__(self, session, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session = session
        self.upload_successful = False

        self.setTitle('Step 8 of {0}: Upload'.format(Constants.STEP_COUNT))

        self.progress_file.setVisible(False)

        self.button_start_upload.clicked.connect(self.start_upload)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Upload the new {0} program [{1}].'
                         .format(Constants.language_display_names[self.field('language').toInt()[0]],
                                 unicode(self.field('name').toString())))
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return -1

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.upload_successful and QWizardPage.isComplete(self)

    def update_ui_state(self):
        pass

    def log(self, message):
        self.list_log.addItem(message)

    def next_step(self, message, increase=1, log=True):
        self.progress_total.setValue(self.progress_total.value() + increase)
        self.label_current_step.setText(message)

        if log:
            self.log(message)

    def upload_error(self, message, defined=True):
        self.wizard().setOption(QWizard.NoCancelButton, False)
        self.log(message)

        if defined:
            pass # FIXME: undefine and purge program?

    def start_upload(self):
        self.button_start_upload.setEnabled(False)
        self.wizard().setOption(QWizard.DisabledBackButtonOnLastPage, True)
        self.wizard().setOption(QWizard.NoCancelButton, True)

        uploads = self.wizard().page(Constants.PAGE_FILES).get_uploads()

        self.progress_total.setRange(0, 6 + len(uploads))

        # define new program
        identifier = str(self.field('identifier').toString())

        self.next_step('Defining new program...', increase=0)

        try:
            program = REDProgram(self.session).define(identifier) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(identifier, e), False)
            return

        self.log('...done')
        self.next_step('Setting custom options...')

        # set custom option: name
        name = unicode(self.field('name').toString())

        try:
            program.set_custom_option_value('name', name) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        # set custom option: language
        language = Constants.api_languages[self.field('language').toInt()[0]]

        try:
            program.set_custom_option_value('language', language) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        self.log('...done')

        # upload files
        self.next_step('Uploading files...', log=False)

        root_directory = unicode(program.root_directory)

        self.progress_file.setRange(0, len(uploads))

        for upload in uploads:
            source_name = upload.source

            self.next_step('Uploading {0}...'.format(source_name))

            self.progress_file.setVisible(False)
            self.progress_file.setRange(0, 0)
            self.progress_file.setValue(0)

            try:
                source_size = os.stat(source_name).st_size
                source = open(source_name, 'rb')
            except Exception as e:
                self.upload_error("...error opening source file '{0}': {1}".format(source_name, e))
                return

            self.progress_file.setRange(0, source_size)

            target_name = os.path.join(root_directory, 'bin', upload.target)

            # FIXME: if upload.target contains a directory then create it before writing

            try:
                target = REDFile(self.session).open(target_name,
                                                    REDFile.FLAG_WRITE_ONLY |
                                                    REDFile.FLAG_CREATE |
                                                    REDFile.FLAG_NON_BLOCKING |
                                                    REDFile.FLAG_TRUNCATE,
                                                    0555, 1000, 1000) # FIXME: async_call, use correct permissions
            except REDError as e:
                self.upload_error("...error opening target file '{0}': {1}".format(target_name, e))
                return

            while True:
                try:
                    data = source.read(1024)
                except Exception as e:
                    self.upload_error("...error reading source file '{0}': {1}".format(source_name, e))
                    return

                if len(data) == 0:
                    break

                try:
                    target.write(data)
                except REDError as e:
                    self.upload_error("...error writing target file '{0}': {1}".format(target_name, e))
                    return

                self.progress_file.setValue(self.progress_file.value() + len(data))

            self.log('...done')
            self.progress_file.setValue(self.progress_file.maximum())

            target.release()
            source.close()

        self.progress_file.setVisible(False)

        # set command
        self.next_step('Setting command...')

        if language == 'java':
            executable, arguments, working_directory = self.wizard().page(Constants.PAGE_JAVA).get_command()
        elif language == 'python':
            executable, arguments, working_directory = self.wizard().page(Constants.PAGE_PYTHON).get_command()

        arguments += self.wizard().page(Constants.PAGE_ARGUMENTS).get_arguments()
        environment = []

        try:
            program.set_command(executable, arguments, environment, working_directory) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        self.log('...done')

        # set stdio redirection
        self.next_step('Setting stdio redirection...')

        stdin_redirection = Constants.api_stdio_redirections[self.field('stdin_redirection').toInt()[0]]
        stdout_redirection = Constants.api_stdio_redirections[self.field('stdout_redirection').toInt()[0]]
        stderr_redirection = Constants.api_stdio_redirections[self.field('stderr_redirection').toInt()[0]]
        stdin_file = unicode(self.field('stdin_file').toString())
        stdout_file = unicode(self.field('stdout_file').toString())
        stderr_file = unicode(self.field('stderr_file').toString())

        try:
            program.set_stdio_redirection(stdin_redirection, stdin_file,
                                          stdout_redirection, stdout_file,
                                          stderr_redirection, stderr_file) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        self.log('...done')

        # set schedule
        self.next_step('Setting schedule...')

        start_condition = Constants.api_schedule_start_condition[self.field('schedule.start_condition').toInt()[0]]
        start_time = self.field('schedule.start_time').toDateTime().toMSecsSinceEpoch() / 1000
        start_delay = self.field('schedule.start_delay').toInt()[0]
        repeat_mode = Constants.api_schedule_repeat_mode[self.field('schedule.repeat_mode').toInt()[0]]
        repeat_interval = self.field('schedule.repeat_interval').toInt()[0]
        # FIXME: handle selection repeat mode

        try:
            program.set_schedule(start_condition, start_time, start_delay,
                                 repeat_mode, repeat_interval, 0, 0, 0, 0, 0, 0) # FIXME: async_call
        except REDError as e:
            self.upload_error('...error: {0}'.format(e))
            return

        self.log('...done')
        self.next_step('Upload successful!')

        self.upload_successful = True
        self.completeChanged.emit()
