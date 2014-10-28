# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_page_stdio.py: Program Wizard Stdio Page

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

from PyQt4.QtGui import QMessageBox
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_stdio import Ui_ProgramPageStdio
import os

class ProgramPageStdio(ProgramPage, Ui_ProgramPageStdio):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle(title_prefix + 'Stdio Redirection')

        self.registerField('stdin_redirection', self.combo_stdin_redirection)
        self.registerField('stdin_file', self.combo_stdin_file, 'currentText')
        self.registerField('stdout_redirection', self.combo_stdout_redirection)
        self.registerField('stdout_file', self.edit_stdout_file)
        self.registerField('stderr_redirection', self.combo_stderr_redirection)
        self.registerField('stderr_file', self.edit_stderr_file)

        self.combo_stdin_redirection.currentIndexChanged.connect(self.update_ui_state)
        self.combo_stdin_redirection.currentIndexChanged.connect(self.emit_complete_changed)
        self.combo_stdout_redirection.currentIndexChanged.connect(self.update_ui_state)
        self.combo_stdout_redirection.currentIndexChanged.connect(self.emit_complete_changed)
        self.combo_stderr_redirection.currentIndexChanged.connect(self.update_ui_state)
        self.combo_stderr_redirection.currentIndexChanged.connect(self.emit_complete_changed)

        self.combo_stdin_file_checker = MandatoryEditableComboBoxChecker(self, self.combo_stdin_file, self.label_stdin_file)
        self.edit_stdout_file_checker = MandatoryLineEditChecker(self, self.edit_stdout_file, self.label_stdout_file)
        self.edit_stderr_file_checker = MandatoryLineEditChecker(self, self.edit_stderr_file, self.label_stderr_file)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify how standard input, output and error of the {0} program [{1}] should be redirected.'
                         .format(Constants.language_display_names[self.get_field(Constants.FIELD_LANGUAGE).toInt()[0]],
                                 unicode(self.get_field(Constants.FIELD_NAME).toString())))
        self.combo_stdin_redirection.setCurrentIndex(Constants.DEFAULT_STDIN_REDIRECTION)
        self.combo_stdout_redirection.setCurrentIndex(Constants.DEFAULT_STDOUT_REDIRECTION)
        self.combo_stderr_redirection.setCurrentIndex(Constants.DEFAULT_STDERR_REDIRECTION)
        self.combo_stdin_file.addItems(self.wizard().available_files)
        self.combo_stdin_file.clearEditText()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            stdin_redirection  = Constants.get_stdin_redirection(program.stdin_redirection)
            stdout_redirection = Constants.get_stdout_redirection(program.stdout_redirection)
            stderr_redirection = Constants.get_stderr_redirection(program.stderr_redirection)

            self.combo_stdin_redirection.setCurrentIndex(stdin_redirection)
            self.combo_stdout_redirection.setCurrentIndex(stdout_redirection)
            self.combo_stderr_redirection.setCurrentIndex(stderr_redirection)

            if program.stdin_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                self.combo_stdin_file.lineEdit().setText(unicode(program.stdin_file_name))

            if program.stdout_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                self.edit_stdout_file.setText(unicode(program.stdout_file_name))

            if program.stdin_redirection == REDProgram.STDIO_REDIRECTION_FILE:
                self.edit_stderr_file.setText(unicode(program.stderr_file_name))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        stdin_redirection  = self.get_field('stdin_redirection').toInt()[0]
        stdout_redirection = self.get_field('stdout_redirection').toInt()[0]
        stderr_redirection = self.get_field('stderr_redirection').toInt()[0]

        if stdin_redirection == Constants.STDIN_REDIRECTION_FILE and \
           not self.combo_stdin_file_checker.valid:
            return False

        if stdout_redirection == Constants.STDOUT_REDIRECTION_FILE and \
           not self.edit_stdout_file_checker.valid:
            return False

        if stderr_redirection == Constants.STDERR_REDIRECTION_FILE and \
           not self.edit_stderr_file_checker.valid:
            return False

        return ProgramPage.isComplete(self)

    def update_ui_state(self):
        stdin_redirection           = self.get_field('stdin_redirection').toInt()[0]
        stdout_redirection          = self.get_field('stdout_redirection').toInt()[0]
        stderr_redirection          = self.get_field('stderr_redirection').toInt()[0]
        stdin_redirection_dev_null  = stdin_redirection  == Constants.STDIN_REDIRECTION_DEV_NULL
        stdin_redirection_pipe      = stdin_redirection  == Constants.STDIN_REDIRECTION_PIPE
        stdin_redirection_file      = stdin_redirection  == Constants.STDIN_REDIRECTION_FILE
        stdout_redirection_dev_null = stdout_redirection == Constants.STDOUT_REDIRECTION_DEV_NULL
        stdout_redirection_file     = stdout_redirection == Constants.STDOUT_REDIRECTION_FILE
        stdout_redirection_log      = stdout_redirection == Constants.STDOUT_REDIRECTION_LOG
        stderr_redirection_dev_null = stderr_redirection == Constants.STDERR_REDIRECTION_DEV_NULL
        stderr_redirection_file     = stderr_redirection == Constants.STDERR_REDIRECTION_FILE
        stderr_redirection_log      = stderr_redirection == Constants.STDERR_REDIRECTION_LOG
        stderr_redirection_stdout   = stderr_redirection == Constants.STDERR_REDIRECTION_STDOUT

        self.label_stdin_file.setVisible(stdin_redirection_file)
        self.combo_stdin_file.setVisible(stdin_redirection_file)
        self.label_stdin_dev_null_help.setVisible(stdin_redirection_dev_null)
        self.label_stdin_pipe_help.setVisible(stdin_redirection_pipe)
        self.label_stdin_file_help.setVisible(stdin_redirection_file)
        self.label_stdout_file.setVisible(stdout_redirection_file)
        self.label_stdout_dev_null_help.setVisible(stdout_redirection_dev_null)
        self.label_stdout_file_help.setVisible(stdout_redirection_file)
        self.label_stdout_log_help.setVisible(stdout_redirection_log)
        self.edit_stdout_file.setVisible(stdout_redirection_file)
        self.label_stderr_file.setVisible(stderr_redirection_file)
        self.edit_stderr_file.setVisible(stderr_redirection_file)
        self.label_stderr_dev_null_help.setVisible(stderr_redirection_dev_null)
        self.label_stderr_file_help.setVisible(stderr_redirection_file)
        self.label_stderr_log_help.setVisible(stderr_redirection_log)
        self.label_stderr_stdout_help.setVisible(stderr_redirection_stdout)

    def emit_complete_changed(self):
        self.completeChanged.emit()

    def apply_program_changes(self):
        program = self.wizard().program

        if program == None:
            return

        stdin_redirection  = Constants.api_stdin_redirections[self.get_field('stdin_redirection').toInt()[0]]
        stdout_redirection = Constants.api_stdout_redirections[self.get_field('stdout_redirection').toInt()[0]]
        stderr_redirection = Constants.api_stderr_redirections[self.get_field('stderr_redirection').toInt()[0]]
        stdin_file         = unicode(self.get_field('stdin_file').toString())
        stdout_file        = unicode(self.get_field('stdout_file').toString())
        stderr_file        = unicode(self.get_field('stderr_file').toString())

        try:
            program.set_stdio_redirection(stdin_redirection, stdin_file,
                                          stdout_redirection, stdout_file,
                                          stderr_redirection, stderr_file) # FIXME: async_call
        except REDError as e:
            QMessageBox.critical(self, 'Edit Error',
                                 u'Could not update stdio redirection of program [{0}]:\n\n{1}'
                                 .format(program.cast_custom_option_value(Constants.FIELD_NAME, unicode, '<unknown>')))
