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

from PyQt4.QtGui import QWizardPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_stdio import Ui_ProgramPageStdio
import os

class ProgramPageStdio(QWizardPage, Ui_ProgramPageStdio):
    def __init__(self, title_prefix='', *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

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
                         .format(Constants.language_display_names[self.field('language').toInt()[0]],
                                 unicode(self.field('name').toString())))
        self.combo_stdin_redirection.setCurrentIndex(Constants.DEFAULT_STDIN_REDIRECTION)
        self.combo_stdout_redirection.setCurrentIndex(Constants.DEFAULT_STDOUT_REDIRECTION)
        self.combo_stderr_redirection.setCurrentIndex(Constants.DEFAULT_STDERR_REDIRECTION)

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            self.combo_stdin_file.addItem(upload.target)

        self.combo_stdin_file.clearEditText()
        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        stdin_redirection = self.field('stdin_redirection').toInt()[0]
        stdout_redirection = self.field('stdout_redirection').toInt()[0]
        stderr_redirection = self.field('stderr_redirection').toInt()[0]

        if stdin_redirection == Constants.STDIN_REDIRECTION_FILE and \
           not self.combo_stdin_file_checker.valid:
            return False

        if stdout_redirection == Constants.STDOUT_REDIRECTION_FILE and \
           not self.edit_stdout_file_checker.valid:
            return False

        if stderr_redirection == Constants.STDERR_REDIRECTION_FILE and \
           not self.edit_stderr_file_checker.valid:
            return False

        return QWizardPage.isComplete(self)

    def update_ui_state(self):
        stdin_redirection           = self.field('stdin_redirection').toInt()[0]
        stdout_redirection          = self.field('stdout_redirection').toInt()[0]
        stderr_redirection          = self.field('stderr_redirection').toInt()[0]
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
