# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_octave.py: Program Wizard Octave Page

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
from brickv.plugin_system.plugins.red.ui_program_page_octave import Ui_ProgramPageOctave

class ProgramPageOctave(ProgramPage, Ui_ProgramPageOctave):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle(title_prefix + 'Octave Configuration')

        self.language = Constants.LANGUAGE_OCTAVE

        self.registerField('octave.version', self.combo_version)
        self.registerField('octave.start_mode', self.combo_start_mode)
        self.registerField('octave.script_file', self.combo_script_file, 'currentText')
        self.registerField('octave.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.combo_script_file_ending.currentIndexChanged.connect(self.update_ui_state)

        self.combo_script_file_ending_checker = ComboBoxFileEndingChecker(self, self.combo_script_file, self.combo_script_file_ending)
        self.combo_script_file_checker = MandatoryEditableComboBoxChecker(self, self.combo_script_file, self.label_script_file)
        self.combo_working_directory_checker = MandatoryEditableComboBoxChecker(self, self.combo_working_directory, self.label_working_directory)

        self.option_list_editor = ListWidgetEditor(self.list_options,
                                                   self.button_add_option,
                                                   self.button_remove_option,
                                                   self.button_up_option,
                                                   self.button_down_option,
                                                   '<new Octave option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the Octave program [{name}] should be executed.')
        self.is_full_image = 'full' in self.wizard().image_version_ref[0]
        self.update_octave_versions()
        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_OCTAVE_START_MODE)

        if self.combo_script_file.count() > 1:
            self.combo_script_file.clearEditText()

        self.combo_script_file_ending_checker.check(False)
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)

        self.combo_working_directory.clear()
        self.combo_working_directory.addItem('.')
        self.combo_working_directory.addItems(self.wizard().available_directories)

        self.option_list_editor.reset_items()
        self.option_list_editor.add_item(unicode('--silent'))

        if not self.is_full_image:
            self.option_list_editor.add_item(unicode('--no-window-system'))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('octave.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if start_mode == Constants.OCTAVE_START_MODE_SCRIPT_FILE and \
           not self.combo_script_file_checker.valid:
            return False

        return self.combo_working_directory_checker.valid and ProgramPage.isComplete(self)

    def update_octave_versions(self):
        def cb_versions(result):
            self.combo_version.clear()
            if result != None:
                version = result.stdout.split('\n')[0].split(' ')[-1]
                try:
                    self.combo_version.addItem(version, QVariant('/usr/bin/octave'))
                    self.combo_version.setEnabled(True)
                    return
                except:
                    pass

            # Could not get versions, we assume that some version
            # of octave 3.6 is installed
            self.combo_version.clear()
            self.combo_version.addItem('3.6', QVariant('/usr/bin/octave'))
            self.combo_version.setEnabled(True)
            self.completeChanged.emit()

        self.wizard().script_manager.execute_script('octave_versions', cb_versions)
        
    def update_ui_state(self):
        start_mode             = self.get_field('octave.start_mode').toInt()[0]
        start_mode_script_file = start_mode == Constants.OCTAVE_START_MODE_SCRIPT_FILE
        show_advanced_options  = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_script_file.setVisible(start_mode_script_file)
        self.label_script_file_ending.setVisible(start_mode_script_file)
        self.combo_script_file.setVisible(start_mode_script_file)
        self.combo_script_file_ending.setVisible(start_mode_script_file)
        self.label_script_file_help.setVisible(start_mode_script_file)
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
        return unicode(self.combo_version.itemData(self.get_field('octave.version').toInt()[0]).toString())

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('octave.start_mode').toInt()[0]

        if self.is_full_image:
            environment.append(unicode('DISPLAY=:0'))

        if start_mode == Constants.OCTAVE_START_MODE_SCRIPT_FILE:
            arguments.append(unicode(self.combo_script_file.currentText()))

        working_directory = unicode(self.get_field('octave.working_directory').toString())

        return executable, arguments, environment, working_directory
