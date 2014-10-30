# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_javascript.py: Program Wizard JavaScript Page

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

from PyQt4.QtCore import QVariant
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_javascript import Ui_ProgramPageJavascript

class ProgramPageJavascript(ProgramPage, Ui_ProgramPageJavascript):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle(title_prefix + 'JavaScript Configuration')

        self.language = Constants.LANGUAGE_JAVASCRIPT

        self.registerField('javascript.version', self.combo_version)
        self.registerField('javascript.start_mode', self.combo_start_mode)
        self.registerField('javascript.script_file', self.combo_script_file, 'currentText')
        self.registerField('javascript.command', self.edit_command)
        self.registerField('javascript.working_directory', self.combo_working_directory, 'currentText')

        self.combo_version.currentIndexChanged.connect(self.update_ui_state)
        self.combo_version.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.combo_script_file_ending.currentIndexChanged.connect(self.update_ui_state)

        self.combo_script_file_ending_checker = ComboBoxFileEndingChecker(self, self.combo_script_file, self.combo_script_file_ending)
        self.combo_script_file_checker = MandatoryEditableComboBoxChecker(self, self.combo_script_file, self.label_script_file)
        self.edit_command_checker = MandatoryLineEditChecker(self, self.edit_command, self.label_command)
        self.combo_working_directory_checker = MandatoryEditableComboBoxChecker(self, self.combo_working_directory, self.label_working_directory)

        self.option_list_editor = ListWidgetEditor(self.list_options,
                                                   self.button_add_option,
                                                   self.button_remove_option,
                                                   self.button_up_option,
                                                   self.button_down_option,
                                                   '<new Node.js option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the JavaScript program [{name}] should be executed.')
        self.update_javascript_versions()
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_JAVASCRIPT_START_MODE)

        if self.combo_script_file.count() > 1:
            self.combo_script_file.clearEditText()

        self.combo_script_file_ending_checker.check(False)
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)

        self.combo_working_directory.clear()
        self.combo_working_directory.addItem('.')
        self.combo_working_directory.addItems(self.wizard().available_directories)
        self.option_list_editor.reset()

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        use_nodejs = self.get_field('javascript.version').toInt()[0] != 0
        start_mode = self.get_field('javascript.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if use_nodejs:
            if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE and \
               not self.combo_script_file_checker.valid:
                return False

            if start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND and \
               not self.edit_command_checker.valid:
                return False

        return self.combo_working_directory_checker.valid and ProgramPage.isComplete(self)

    def update_javascript_versions(self):
        def cb_versions(result):
            self.combo_version.clear()
            if result != None:
                version = result.stdout.split('\n')[0]
                node_version_str = 'Server-side (Node.js {0})'.format(version)
                try:
                    self.combo_version.addItem('Client-side (Browser)', QVariant('/bin/true'))
                    self.combo_version.addItem(node_version_str, QVariant('/usr/local/bin/node'))
                    self.combo_version.setEnabled(True)
                    return
                except:
                    pass

            # Could not get versions, we assume that some version
            # of nodejs is installed
            self.combo_version.clear()
            self.combo_version.addItem('Client-side (Browser)', QVariant('/bin/true'))
            self.combo_version.addItem('Server-side (Node.js)', QVariant('/usr/local/bin/node'))
            self.combo_version.setEnabled(True)
            self.completeChanged.emit()

        self.wizard().script_manager.execute_script('javascript_versions', cb_versions)

    def update_ui_state(self):
        use_nodejs             = self.get_field('javascript.version').toInt()[0] != 0
        start_mode             = self.get_field('javascript.start_mode').toInt()[0]
        start_mode_script_file = (start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE) and use_nodejs
        start_mode_command     = (start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND) and use_nodejs
        show_advanced_options  = (self.check_show_advanced_options.checkState() == Qt.Checked) and use_nodejs

        self.label_start_mode.setVisible(use_nodejs)
        self.combo_start_mode.setVisible(use_nodejs)
        self.label_script_file.setVisible(start_mode_script_file)
        self.label_script_file_ending.setVisible(start_mode_script_file)
        self.combo_script_file.setVisible(start_mode_script_file)
        self.combo_script_file_ending.setVisible(start_mode_script_file)
        self.label_script_file_help.setVisible(start_mode_script_file)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)
        self.line.setVisible(use_nodejs)
        self.check_show_advanced_options.setVisible(use_nodejs)
        self.label_working_directory.setVisible(show_advanced_options)
        self.combo_working_directory.setVisible(show_advanced_options)
        self.label_options.setVisible(show_advanced_options)
        self.list_options.setVisible(show_advanced_options)
        self.label_options_help.setVisible(show_advanced_options)
        self.button_add_option.setVisible(show_advanced_options)
        self.button_remove_option.setVisible(show_advanced_options)
        self.button_up_option.setVisible(show_advanced_options)
        self.button_down_option.setVisible(show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('javascript.version').toInt()[0]).toString())

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('javascript.start_mode').toInt()[0]

        if start_mode == Constants.JAVASCRIPT_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))
        elif start_mode == Constants.JAVASCRIPT_START_MODE_COMMAND:
            arguments.append('-e')
            arguments.append(unicode(self.edit_command.text()))

        working_directory = unicode(self.get_field('javascript.working_directory').toString())

        return executable, arguments, environment, working_directory
