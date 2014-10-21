# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_arguments.py: New Program Wizard Arguments Page

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
from brickv.plugin_system.plugins.red.new_program_utils import Constants, ListWidgetEditor
from brickv.plugin_system.plugins.red.ui_new_program_arguments import Ui_NewProgramArguments

class NewProgramArguments(QWizardPage, Ui_NewProgramArguments):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 4 of {0}: Arguments'.format(Constants.STEP_COUNT))

        self.argument_list_editor = ListWidgetEditor(self.list_arguments,
                                                     self.button_add_argument,
                                                     self.button_up_argument,
                                                     self.button_down_argument,
                                                     self.button_remove_argument,
                                                     '<new argument {0}>')

    # overrides QWizardPage.initializePage
    def initializePage(self):
        language = self.field('language').toInt()[0]

        self.setSubTitle(u'Specify the arguments to be passed to the new {0} program [{1}].'
                         .format(Constants.language_names[language],
                                 unicode(self.field('name').toString())))
        self.label_arguments_help.setText(Constants.arguments_help[language])
        self.argument_list_editor.remove_all_items()
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        return Constants.PAGE_STDIO

    def update_ui_state(self):
        self.argument_list_editor.update_ui_state()

    def emit_complete_changed(self):
        self.completeChanged.emit()

    def get_arguments(self):
        arguments = []

        for row in range(self.list_arguments.count()):
            arguments.append(self.list_arguments.item(row).text())

        return arguments
