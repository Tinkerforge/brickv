# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import QVariant
from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_vbnet import Ui_ProgramPageVBNET

class ProgramPageVBNET(ProgramPage, Ui_ProgramPageVBNET):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

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
                                                                 self.button_up_option,
                                                                 self.button_down_option,
                                                                 '<new Mono option {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify how the {language} program [{name}] should be executed.')

        self.update_combo_version('mono', self.combo_version)

        self.combo_start_mode.setCurrentIndex(Constants.DEFAULT_VBNET_START_MODE)
        self.combo_executable_selector.reset()
        self.check_show_advanced_options.setCheckState(Qt.Unchecked)
        self.combo_working_directory_selector.reset()
        self.option_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            # start mode
            start_mode_api_name = program.cast_custom_option_value('vbnet.start_mode', unicode, '<unknown>')
            start_mode          = Constants.get_vbnet_start_mode(start_mode_api_name)

            self.combo_start_mode.setCurrentIndex(start_mode)

            # executable
            self.combo_executable_selector.set_current_text(program.cast_custom_option_value('vbnet.executable', unicode, ''))

            # working directory
            self.combo_working_directory_selector.set_current_text(unicode(program.working_directory))

            # options
            self.option_list_editor.clear()

            for option in program.cast_custom_option_value_list('vbnet.options', unicode, []):
                self.option_list_editor.add_item(option)

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        executable = self.get_executable()
        start_mode = self.get_field('vbnet.start_mode').toInt()[0]

        if len(executable) == 0:
            return False

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE and \
           not self.combo_executable_selector.complete:
            return False

        return self.combo_working_directory_selector.complete and ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        start_mode            = self.get_field('vbnet.start_mode').toInt()[0]
        start_mode_executable = start_mode == Constants.VBNET_START_MODE_EXECUTABLE
        show_advanced_options = self.check_show_advanced_options.checkState() == Qt.Checked

        self.combo_executable_selector.set_visible(start_mode_executable)
        self.combo_working_directory_selector.set_visible(show_advanced_options)
        self.option_list_editor.set_visible(show_advanced_options)
        self.label_spacer.setVisible(not show_advanced_options)

        self.option_list_editor.update_ui_state()

    def get_executable(self):
        return unicode(self.combo_version.itemData(self.get_field('vbnet.version').toInt()[0]).toString())

    def get_html_summary(self):
        version           = self.get_field('vbnet.version').toInt()[0]
        start_mode        = self.get_field('vbnet.start_mode').toInt()[0]
        executable        = self.get_field('vbnet.executable').toString()
        working_directory = self.get_field('vbnet.working_directory').toString()
        options           = ' '.join(self.option_list_editor.get_items())

        html  = u'Mono Version: {0}<br/>'.format(Qt.escape(self.combo_version.itemText(version)))
        html += u'Start Mode: {0}<br/>'.format(Qt.escape(Constants.vbnet_start_mode_display_names[start_mode]))

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE:
            html += u'Executable: {0}<br/>'.format(Qt.escape(executable))

        html += u'Working Directory: {0}<br/>'.format(Qt.escape(working_directory))
        html += u'Mono Options: {0}<br/>'.format(Qt.escape(options))

        return html

    def get_custom_options(self):
        return {
            'vbnet.start_mode': Constants.vbnet_start_mode_api_names[self.get_field('vbnet.start_mode').toInt()[0]],
            'vbnet.executable': unicode(self.get_field('vbnet.executable').toString()),
            'vbnet.options':    self.option_list_editor.get_items()
        }

    def get_command(self):
        executable  = self.get_executable()
        arguments   = self.option_list_editor.get_items()
        environment = []
        start_mode  = self.get_field('vbnet.start_mode').toInt()[0]

        if start_mode == Constants.VBNET_START_MODE_EXECUTABLE:
            arguments.append(unicode(self.get_field('vbnet.executable').toString()))

        working_directory = unicode(self.get_field('vbnet.working_directory').toString())

        return executable, arguments, environment, working_directory

    def apply_program_changes(self):
        self.apply_program_custom_options_and_command_changes()
