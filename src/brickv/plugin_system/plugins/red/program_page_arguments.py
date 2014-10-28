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

from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_wizard_utils import *
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

        self.argument_list_editor = ListWidgetEditor(self.list_arguments,
                                                     self.button_add_argument,
                                                     self.button_remove_argument,
                                                     self.button_up_argument,
                                                     self.button_down_argument,
                                                     '<new argument {0}>')

        self.environment_list_editor = TreeWidgetEditor(self.tree_environment,
                                                        self.button_add_environment_variable,
                                                        self.button_remove_environment_variable,
                                                        self.button_up_environment_variable,
                                                        self.button_down_environment_variable,
                                                        ['<new name {0}>', '<new value {0}>'])

    # overrides QWizardPage.initializePage
    def initializePage(self):
        language = self.get_field(Constants.FIELD_LANGUAGE).toInt()[0]

        self.setSubTitle(u'Specify the arguments to be passed to the {0} program [{1}] and its environment.'
                         .format(Constants.language_display_names[language],
                                 unicode(self.get_field(Constants.FIELD_NAME).toString())))
        self.label_arguments_help.setText(Constants.arguments_help[language])
        self.argument_list_editor.reset_items()
        self.check_show_environment.setCheckState(Qt.Unchecked)
        self.label_environment_help.setText(Constants.environment_help[language])
        self.environment_list_editor.reset_items()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            try:
                editable_arguments_offset = max(int(unicode(self.wizard().program.custom_options.get('editable_arguments_offset', '0'))), 0)
            except ValueError:
                editable_arguments_offset = 0

            for argument in self.wizard().program.arguments.items[editable_arguments_offset:]:
                self.argument_list_editor.add_item(unicode(argument))

            for variable in self.wizard().program.environment.items:
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

        self.label_environment.setVisible(show_environment)
        self.tree_environment.setVisible(show_environment)
        self.label_environment_help.setVisible(show_environment)
        self.button_add_environment_variable.setVisible(show_environment)
        self.button_remove_environment_variable.setVisible(show_environment)
        self.button_up_environment_variable.setVisible(show_environment)
        self.button_down_environment_variable.setVisible(show_environment)

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
