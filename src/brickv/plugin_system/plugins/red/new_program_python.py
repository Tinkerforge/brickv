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
from brickv.plugin_system.plugins.red.new_program_utils import *
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
        self.registerField('python.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_script_file_checker = MandatoryEditableComboBoxChecker(self, self.combo_script_file, self.label_script_file)
        self.edit_module_name_checker = MandatoryLineEditChecker(self, self.edit_module_name, self.label_module_name)
        self.edit_command_checker = MandatoryLineEditChecker(self, self.edit_command, self.label_command)
        self.combo_working_directory_checker = MandatoryEditableComboBoxChecker(self, self.combo_working_directory, self.label_working_directory)

        self.option_list_editor = ListWidgetEditor(self.list_options,
                                                   self.button_add_option,
                                                   self.button_remove_option,
                                                   self.button_up_option,
                                                   self.button_down_option,
                                                   '<new Python option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify how the new Python program [{0}] should be executed.'
                         .format(unicode(self.field('name').toString())))
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_PYTHON_START_MODE)
        self.combo_script_file.clear()

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            if upload.target.lower().endswith('.py'):
                self.combo_script_file.addItem(upload.target)

        if self.combo_script_file.count() > 1:
            self.combo_script_file.clearEditText()

        self.combo_working_directory.clear()
        self.combo_working_directory.addItem('.')

        for upload in self.wizard().page(Constants.PAGE_FILES).get_uploads():
            directory = os.path.split(upload.target)[0]

            if len(directory) > 0:
                self.combo_working_directory.addItem(directory)

        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_ARGUMENTS

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.field('python.start_mode').toInt()[0]

        if start_mode == Constants.PYTHON_START_MODE_SCRIPT_FILE and \
           not self.combo_script_file_checker.valid:
            return False

        if start_mode == Constants.PYTHON_START_MODE_MODULE_NAME and \
           not self.edit_module_name_checker.valid:
            return False

        if start_mode == Constants.PYTHON_START_MODE_COMMAND and \
           not self.edit_command_checker.valid:
            return False

        return self.combo_working_directory_checker.valid and QWizardPage.isComplete(self)

    def update_ui_state(self):
        start_mode = self.field('python.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.PYTHON_START_MODE_SCRIPT_FILE
        start_mode_module_name = start_mode == Constants.PYTHON_START_MODE_MODULE_NAME
        start_mode_command = start_mode == Constants.PYTHON_START_MODE_COMMAND
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_script_file.setVisible(start_mode_script_file)
        self.combo_script_file.setVisible(start_mode_script_file)
        self.label_script_file_help.setVisible(start_mode_script_file)
        self.label_module_name.setVisible(start_mode_module_name)
        self.edit_module_name.setVisible(start_mode_module_name)
        self.label_module_name_help.setVisible(start_mode_module_name)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)
        self.label_working_directory.setVisible(show_advanced_options)
        self.combo_working_directory.setVisible(show_advanced_options)
        self.label_options.setVisible(show_advanced_options)
        self.list_options.setVisible(show_advanced_options)
        self.label_options_help.setVisible(show_advanced_options)
        self.button_add_option.setVisible(show_advanced_options)
        self.button_remove_option.setVisible(show_advanced_options)
        self.button_up_option.setVisible(show_advanced_options)
        self.button_down_option.setVisible(show_advanced_options)

    def get_command(self):
        executable = '/usr/bin/python2'
        arguments = self.option_list_editor.get_items()
        start_mode = self.field('python.start_mode').toInt()[0]

        if start_mode == Constants.PYTHON_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))
        elif start_mode == Constants.PYTHON_START_MODE_MODULE_NAME:
            arguments.append('-m')
            arguments.append(unicode(self.edit_module_name.text()))
        elif start_mode == Constants.PYTHON_START_MODE_COMMAND:
            arguments.append('-c')
            arguments.append(unicode(self.edit_command.text()))

        working_directory = unicode(self.field('python.working_directory').toString())

        return executable, arguments, working_directory
