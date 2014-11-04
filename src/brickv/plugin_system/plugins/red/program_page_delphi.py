# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

program_page_delphi.py: Program Wizard Delphi Page

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

from PyQt4.QtCore import QVariant, pyqtProperty, QObject, pyqtSignal
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_delphi import Ui_ProgramPageDelphi
import os

def get_fpc_versions(script_manager, callback):
    def cb_versions(result):
        if result != None:
            try:
                version = result.stdout.split('\n')[0].split(' ')[-1]
                callback([ExecutableVersion('/usr/bin/fpc', version)])
                return
            except:
                pass

        # Could not get versions, we assume that some version of fpc 2.6 is installed
        callback([ExecutableVersion('/usr/bin/fpc', '2.6')])

    script_manager.execute_script('fpc_versions', cb_versions)


class ProgramPageDelphi(ProgramPage, Ui_ProgramPageDelphi):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_DELPHI

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('delphi.start_mode', self.combo_start_mode)
        self.registerField('delphi.file', self.combo_file, 'currentText')
        self.registerField('delphi.executable', self.combo_executable, 'currentText')
        self.registerField('delphi.working_directory', self.combo_working_directory, 'currentText')
        self.registerField('delphi.compile_options', self, 'get_compile_options')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(lambda: self.completeChanged.emit())
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)

        self.combo_executable_selector        = MandatoryEditableComboBoxChecker(self,
                                                                                 self.combo_executable,
                                                                                 self.label_executable)
        self.combo_executable_checker         = ComboBoxFileEndingChecker(self,
                                                                          self.combo_executable)
        self.combo_file_selector              = MandatoryTypedFileSelector(self,
                                                                           self.label_file,
                                                                           self.combo_file,
                                                                           self.label_file_type,
                                                                           self.combo_file_type,
                                                                           self.label_file_help)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.combo_working_directory,
                                                                           self.label_working_directory)
        self.option_list_editor               = ListWidgetEditor(self.label_options,
                                                                 self.list_options,
                                                                 self.label_options_help,
                                                                 self.button_add_option,
                                                                 self.button_remove_option,
                                                                 self.button_up_option,
                                                                 self.button_down_option,
                                                                 '<new FPC option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        def cb_fpc_versions(versions):
            self.combo_start_mode.clear()
            self.combo_start_mode.addItem('Executable')
            self.combo_start_mode.addItem('Compile on RED Brick (FPC {0})'.format(versions[0].version), QVariant(versions[0].executable))
            self.completeChanged.emit()

        self.get_executable_versions('fpc', cb_fpc_versions)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_DELPHI_START_MODE)
        self.combo_executable_checker.check(False)
        self.combo_file_selector.reset()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        start_mode = self.get_field('delphi.start_mode').toInt()[0]

        if start_mode == Constants.DELPHI_START_MODE_EXECUTABLE and \
           not self.combo_executable_selector.complete:
            return False
        elif start_mode == Constants.DELPHI_START_MODE_COMPILE and \
           not self.combo_file_selector.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    def update_ui_state(self):
        start_mode            = self.get_field('delphi.start_mode').toInt()[0]
        start_mode_executable = start_mode == Constants.DELPHI_START_MODE_EXECUTABLE
        start_mode_compile    = start_mode == Constants.DELPHI_START_MODE_COMPILE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.label_start_compile_help.setVisible(start_mode_compile)
        self.label_start_executable_help.setVisible(start_mode_executable)
        self.label_file.setVisible(start_mode_compile)
        self.label_file_help.setVisible(start_mode_compile)
        self.combo_file.setVisible(start_mode_compile)
        self.label_file_type.setVisible(start_mode_compile)
        self.combo_file_type.setVisible(start_mode_compile)
        self.label_executable.setVisible(start_mode_executable)
        self.label_executable_help.setVisible(start_mode_executable)
        self.combo_executable.setVisible(start_mode_executable)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options and start_mode_compile)

        self.option_list_editor.update_ui_state()

    @pyqtProperty(str)
    def get_compile_options(self):
        return ' '.join(self.option_list_editor.get_items())

    def get_command(self):
        arguments         = self.option_list_editor.get_items()
        environment       = []
        working_directory = unicode(self.get_field('delphi.working_directory').toString())
        start_mode        = self.get_field('delphi.start_mode').toInt()[0]

        if start_mode == Constants.DELPHI_START_MODE_EXECUTABLE:
            executable = unicode(self.get_field('delphi.executable').toString())

            if not executable.startswith('/'):
                executable = os.path.join('./', executable)
        elif start_mode == Constants.DELPHI_START_MODE_COMPILE:
            to_compile = unicode('./{0}'.format(self.get_field('delphi.file').toString()))
            executable = os.path.splitext(to_compile)[0]

        return executable, arguments, environment, working_directory
