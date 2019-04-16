# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_page_vbnet.py: Program Wizard Visual Basic .NET Page

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

import html

from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_vbnet import Ui_ProgramPageVBNET

class ProgramPageVBNET(ProgramPage, Ui_ProgramPageVBNET):
    def __init__(self, title_prefix=''):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.language = Constants.LANGUAGE_VBNET

        self.setTitle('{0}{1} Configuration'.format(title_prefix, Constants.language_display_names[self.language]))

        self.registerField('vbnet.version', self.combo_version)
        self.registerField('vbnet.start_mode', self.combo_start_mode)
        self.registerField('vbnet.executable', self.combo_executable, 'currentText')
        self.registerField('vbnet.working_directory', self.combo_working_directory, 'currentText')

        self.combo_start_mode.currentIndexChanged.connect(self.update_ui_state)
        self.combo_start_mode.currentIndexChanged.connect(self.completeChanged.emit)
        self.check_show_advanced_options.stateChanged.connect(self.update_ui_state)
        self.label_spacer.setText('')

        self.combo_executable_selector        = MandatoryTypedFileSelector(self,
                                                                           self.label_executable,
                                                                           self.combo_executable,
                                                                           self.label_executable_type,
                                                                           self.combo_executable_type,
                                                                           self.label_executable_help)
        self.combo_working_directory_selector = MandatoryDirectorySelector(self,
                                                                           self.label_working_directory,
                                                                           self.combo_working_directory)
        self.option_list_editor               = ListWidgetEditor(self.label_options,
                                                                 self.list_options,
                                                                 self.label_options_help,
                                                                 self.button_add_option,
                                                                 self.button_remove_option,
                                                                 self.button_edit_option,
                                                                 self.button_up_option,
                                                                 self.button_down_option,
                                                                 '<new Mono option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title('Specify how the {language} program [{name}] should be executed.')

        self.update_combo_version('mono', self.combo_version)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_VBNET_START_MODE)
        self.combo_executable_selector.reset()
        self.check_show_advanced_options.setChecked(False)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        program = self.wizard().program

        if program != None:
            # start mode
            start_mode_api_name = program.cast_custom_option_value('vbnet.start_mode', str, '<unknown>')
            start_mode          = Constants.get_vbnet_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # executable
            self.combo_executable_selector.set_current_text(program.cast_custom_option_value('vbnet.executable', str, ''))

            # working directory
            self.combo_working_directory_selector.set_current_text(program.working_directory)

            # options
            self.option_list_editor.clear()

            for option in program.cast_custom_option_value_list('vbnet.options', str, []):
                self.option_list_editor.add_item(option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('vbnet.start_mode')

        if len(executable) == 0:
            return False

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE and \
           not self.combo_executable_selector.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('vbnet.start_mode')
        start_mode_executable = start_mode == Constants.VBNET_START_MODE_EXECUTABLE
        show_advanced_options = self.check_show_advanced_options.isChecked()

        self.combo_executable_selector.set_visible(start_mode_executable)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)
        self.label_spacer.setVisible(not show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return self.combo_version.itemData(self.get_field('vbnet.version'))

    def get_html_summary(self):
        version           = self.get_field('vbnet.version')
        start_mode        = self.get_field('vbnet.start_mode')
        executable        = self.get_field('vbnet.executable')
        working_directory = self.get_field('vbnet.working_directory')
        options           = ' '.join(self.option_list_editor.get_items())

        html_text  = 'Mono Version: {0}<br/>'.format(html.escape(self.combo_version.itemText(version)))
        html_text += 'Start Mode: {0}<br/>'.format(html.escape(Constants.vbnet_start_mode_display_names[start_mode]))

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE:
            html_text += 'Executable: {0}<br/>'.format(html.escape(executable))

        html_text += 'Working Directory: {0}<br/>'.format(html.escape(working_directory))
        html_text += 'Mono Options: {0}<br/>'.format(html.escape(options))

        return html_text

    def get_custom_options(self):
        return {
            'vbnet.start_mode': Constants.vbnet_start_mode_api_names[self.get_field('vbnet.start_mode')],
            'vbnet.executable': self.get_field('vbnet.executable'),
            'vbnet.options':    self.option_list_editor.get_items()
        }

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('vbnet.start_mode')

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE:
            arguments.append(self.get_field('vbnet.executable'))

        working_directory = self.get_field('vbnet.working_directory')

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
