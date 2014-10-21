# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_python.py: New Program Wizard Python Page

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
from brickv.plugin_system.plugins.red.new_program_utils import Constants, MandatoryLineEditChecker
from brickv.plugin_system.plugins.red.ui_new_program_python import Ui_NewProgramPython

class NewProgramPython(QWizardPage, Ui_NewProgramPython):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 4 of {0}: Python Configuration'.format(Constants.STEP_COUNT))

        self.registerField('python.version', self.combo_version)
        self.registerField('python.start_mode', self.combo_start_mode)
        self.registerField('python.script_file', self.combo_script_file, 'currentText')
        self.registerField('python.module_name', self.edit_module_name)
        self.registerField('python.command', self.edit_command)

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.emit_complete_changed)
        self.combo_script_file.currentIndexChanged.connect(self.emit_complete_changed)
        self.combo_script_file.editTextChanged.connect(self.emit_complete_changed)
        self.edit_module_name.textChanged.connect(self.emit_complete_changed)
        self.edit_command.textChanged.connect(self.emit_complete_changed)

        self.combo_script_file_checker = MandatoryLineEditChecker(self.combo_script_file.lineEdit(), self.label_script_file)
        self.edit_module_name_checker = MandatoryLineEditChecker(self.edit_module_name, self.label_module_name)
        self.edit_command_checker = MandatoryLineEditChecker(self.edit_command, self.label_command)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify how the new Python program [{0}] should be executed.'
                         .format(str(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_PYTHON_START_MODE)
        self.combo_script_file.clear()

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            if upload.target.lower().endswith('.py'):
                self.combo_script_file.addItem(upload.target)

        if self.combo_script_file.count() > 1:
            self.combo_script_file.clearEditText()

        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_ARGUMENTS

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.field('python.start_mode').toInt()[0]

        if start_mode == Constants.PYTHON_START_MODE_SCRIPT_FILE and \
           len(self.combo_script_file.currentText()) == 0:
            return False

        if start_mode == Constants.PYTHON_START_MODE_MODULE_NAME and \
           len(self.edit_module_name.text()) == 0:
            return False

        if start_mode == Constants.PYTHON_START_MODE_COMMAND and \
           len(self.edit_command.text()) == 0:
            return False

        return QWizardPage.isComplete(self)

    def update_ui_state(self):
        start_mode = self.field('python.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.PYTHON_START_MODE_SCRIPT_FILE
        start_mode_module_name = start_mode == Constants.PYTHON_START_MODE_MODULE_NAME
        start_mode_command = start_mode == Constants.PYTHON_START_MODE_COMMAND

        self.label_script_file.setVisible(start_mode_script_file)
        self.combo_script_file.setVisible(start_mode_script_file)
        self.label_script_file_help.setVisible(start_mode_script_file)
        self.label_module_name.setVisible(start_mode_module_name)
        self.edit_module_name.setVisible(start_mode_module_name)
        self.label_module_name_help.setVisible(start_mode_module_name)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)

    def emit_complete_changed(self):
        self.completeChanged.emit()
