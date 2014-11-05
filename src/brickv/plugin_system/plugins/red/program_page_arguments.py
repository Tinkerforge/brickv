# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_page_arguments.py: Program Wizard Arguments Page

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
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_arguments import Ui_ProgramPageArguments

class ProgramPageArguments(ProgramPage, Ui_ProgramPageArguments):
    def __init__(self, title_prefix='', *args, **kwargs):
        ProgramPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.environment_is_valid = True

        self.setTitle(title_prefix + 'Arguments and Environment')

        self.tree_environment.setColumnWidth(0, 150)
        self.check_show_environment.stateChanged.connect(self.update_ui_state)
        self.tree_environment.itemChanged.connect(self.check_environment)

        self.argument_list_editor = ListWidgetEditor(self.label_arguments,
                                                     self.list_arguments,
                                                     self.label_arguments_help,
                                                     self.button_add_argument,
                                                     self.button_remove_argument,
                                                     self.button_up_argument,
                                                     self.button_down_argument,
                                                     '<new argument {0}>')

        self.environment_list_editor = TreeWidgetEditor(self.label_environment,
                                                        self.tree_environment,
                                                        self.label_environment_help,
                                                        self.button_add_environment_variable,
                                                        self.button_remove_environment_variable,
                                                        self.button_up_environment_variable,
                                                        self.button_down_environment_variable,
                                                        ['<new name {0}>', '<new value {0}>'])

    # overrides QWizardPage.initializePage
    def initializePage(self):
        language = self.get_field('language').toInt()[0]

        self.set_formatted_sub_title(u'Specify the arguments to be passed to the {language} program [{name}] and its environment.')

        self.label_arguments_help.setText(Constants.arguments_help[language])
        self.argument_list_editor.reset()
        self.check_show_environment.setCheckState(Qt.Unchecked)
        self.label_environment_help.setText('This list of environment variables will be set for the {0} program.'
                                            .format(Constants.language_display_names[language]))
        self.environment_list_editor.reset()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            program = self.wizard().program

            self.argument_list_editor.clear()
            editable_arguments_offset = max(program.cast_custom_option_value('editable_arguments_offset', int, 0), 0)

            for argument in program.arguments.items[editable_arguments_offset:]:
                self.argument_list_editor.add_item(unicode(argument))

            self.environment_list_editor.clear()
            editable_environment_offset = max(program.cast_custom_option_value('editable_environment_offset', int, 0), 0)

            for variable in program.environment.items[editable_environment_offset:]:
                variable = unicode(variable)
                i = variable.find('=')

                if i < 0:
                    name = variable
                    value = ''
                else:
                    name = variable[:i]
                    value = variable[i + 1:]

                self.environment_list_editor.add_item([name, value])

        self.update_ui_state()

    # overrides QWizardPage.isComplete
    def isComplete(self):
        return self.environment_is_valid and ProgramPage.isComplete(self)

    def update_ui_state(self):
        show_environment = self.check_show_environment.checkState() == Qt.Checked

        self.environment_list_editor.set_visible(show_environment)

        self.argument_list_editor.update_ui_state()
        self.environment_list_editor.update_ui_state()

    def check_environment(self):
        environment_was_valid = self.environment_is_valid
        self.environment_is_valid = True

        for item in self.environment_list_editor.get_items():
            if len(item[0]) == 0 or '=' in item[0]:
                self.environment_is_valid = False

        if self.environment_is_valid:
            self.label_environment.setStyleSheet('')
        else:
            self.label_environment.setStyleSheet('QLabel { color : red }')

        if environment_was_valid != self.environment_is_valid:
            self.completeChanged.emit()

    def get_arguments(self):
        return self.argument_list_editor.get_items()

    def get_environment(self):
        environment = []

        for variable in self.environment_list_editor.get_items():
            environment.append(u'{0}={1}'.format(variable[0], variable[1]))

        return environment

    def apply_program_changes(self):
        program = self.wizard().program

        if program == None:
            return

        executable                  = program.executable
        editable_arguments_offset   = max(program.cast_custom_option_value('editable_arguments_offset', int, 0), 0)
        arguments                   = program.arguments.items[:editable_arguments_offset]
        editable_environment_offset = max(program.cast_custom_option_value('editable_environment_offset', int, 0), 0)
        environment                 = program.environment.items[:editable_environment_offset]
        working_directory           = program.working_directory

        arguments   += self.get_arguments()
        environment += self.get_environment()

        try:
            program.set_command(executable, arguments, environment, working_directory) # FIXME: async_call
        except REDError as e:
            QMessageBox.critical(self, 'Edit Error',
                                 u'Could not update arguments and environment of program [{0}]:\n\n{1}'
                                 .format(program.cast_custom_option_value('name', unicode, '<unknown>')))
