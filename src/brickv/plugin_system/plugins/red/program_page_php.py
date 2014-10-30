# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_php.py: Program Wizard PHP Page

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
from brickv.plugin_system.plugins.red.ui_program_page_php import Ui_ProgramPagePHP

class ProgramPagePHP(ProgramPage, Ui_ProgramPagePHP):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle(title_prefix + 'PHP Configuration')
        
        self.language = Constants.LANGUAGE_PHP

        self.registerField('php.version', self.combo_version)
        self.registerField('php.start_mode', self.combo_start_mode)
        self.registerField('php.script_file', self.combo_script_file, 'currentText')
        self.registerField('php.command', self.edit_command)
        self.registerField('php.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.combo_script_file_ending.currentIndexChanged.connect(self.update_ui_state)

        self.combo_script_file_ending_checker = ComboBoxFileEndingChecker(self, self.combo_script_file, self.combo_script_file_ending)
        self.combo_script_file_checker        = MandatoryEditableComboBoxChecker(self, self.combo_script_file, self.label_script_file)
        self.edit_command_checker             = MandatoryLineEditChecker(self, self.edit_command, self.label_command)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self, self.combo_working_directory, self.label_working_directory)

        self.option_list_editor = ListWidgetEditor(self.label_options,
                                                   self.list_options,
                                                   self.label_options_help,
                                                   self.button_add_option,
                                                   self.button_remove_option,
                                                   self.button_up_option,
                                                   self.button_down_option,
                                                   '<new PHP option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify how the PHP program [{0}] should be executed.'
                         .format(unicode(self.get_field(Constants.FIELD_NAME).toString())))
        self.update_php_versions()
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_PHP_START_MODE)

        if self.combo_script_file.count() > 1:
            self.combo_script_file.clearEditText()

        self.combo_script_file_ending_checker.check(False)
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)

        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('php.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if start_mode == Constants.PHP_START_MODE_SCRIPT_FILE and \
           not self.combo_script_file_checker.valid:
            return False

        if start_mode == Constants.PHP_START_MODE_COMMAND and \
           not self.edit_command_checker.valid:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_php_versions(self):
        def cb_versions(result):
            self.combo_version.clear()
            if result != None:
                version = result.stdout.split('\n')[0].split(' ')[1]
                try:
                    self.combo_version.addItem(version, QVariant('/usr/bin/php'))
                    self.combo_version.setEnabled(True)
                    return
                except:
                    pass

            # Could not get versions, we assume that some version
            # of php 1.9 is installed
            self.combo_version.clear()
            self.combo_version.addItem('5', QVariant('/usr/bin/php'))
            self.combo_version.setEnabled(True)
            self.completeChanged.emit()

        self.wizard().script_manager.execute_script('php_versions', cb_versions)
        
    def update_ui_state(self):
        start_mode             = self.get_field('php.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.PHP_START_MODE_SCRIPT_FILE
        start_mode_command     = start_mode == Constants.PHP_START_MODE_COMMAND
        show_advanced_options  = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_script_file.setVisible(start_mode_script_file)
        self.label_script_file_ending.setVisible(start_mode_script_file)
        self.combo_script_file.setVisible(start_mode_script_file)
        self.combo_script_file_ending.setVisible(start_mode_script_file)
        self.label_script_file_help.setVisible(start_mode_script_file)
        self.label_command.setVisible(start_mode_command)
        self.edit_command.setVisible(start_mode_command)
        self.label_command_help.setVisible(start_mode_command)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('php.version').toInt()[0]).toString())

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('php.start_mode').toInt()[0]

        if start_mode == Constants.PHP_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))
        elif start_mode == Constants.PHP_START_MODE_COMMAND:
            arguments.append('-r')
            arguments.append(unicode(self.edit_command.text()))

        working_directory = unicode(self.get_field('php.working_directory').toString())

        return executable, arguments, environment, working_directory
