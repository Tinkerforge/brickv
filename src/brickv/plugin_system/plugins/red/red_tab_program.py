# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Matthias <matthias@tinkerforge.com>

red_tab_program.py: RED program tab implementation

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

from PyQt4.QtGui import QWidget, QMessageBox
from brickv.plugin_system.plugins.red.ui_red_tab_program import Ui_REDTabProgram
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_wizard_new import ProgramWizardNew

class REDTabProgram(QWidget, Ui_REDTabProgram):
    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)

        self.session = None
        self.programs = {}
        self.new_program_wizard = None

        self.list_programs.itemSelectionChanged.connect(self.update_ui_state)
        self.button_new.clicked.connect(self.show_new_program_wizard)
        self.button_delete.clicked.connect(self.purge_selected_program)

        self.update_ui_state()

    def tab_on_focus(self):
        self.programs = {}
        self.list_programs.clear()

        for program in get_programs(self.session).items:
            self.programs[str(program.identifier)] = program

            self.list_programs.addItem(str(program.identifier))

    def tab_off_focus(self):
        pass

    def update_ui_state(self):
        has_selection = len(self.list_programs.selectedItems()) > 0

        self.button_delete.setEnabled(has_selection)

    def show_new_program_wizard(self):
        self.new_program_wizard = ProgramWizardNew(self.session, self.programs.keys())
        self.new_program_wizard.show()

    def purge_selected_program(self):
        selected_items = self.list_programs.selectedItems()

        if len(selected_items) == 0:
            return

        identifier = str(selected_items[0].text())
        program = self.programs[identifier]
        name = identifier # FIXME: get program name

        button = QMessageBox.question(self, 'Delete Program',
                                      u'Deleting program [{0}] is irreversible. All files of this program will be deleted.'.format(name),
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if button == QMessageBox.Ok:
            try:
                program.purge() # FIXME: async_call
            except REDError as e:
                QMessageBox.critical(self, 'Delete Error',
                                     u'Could not delete program [{0}]:\n\n{1}'.format(name, str(e)))
                return

            QMessageBox.information(self, 'Delete Successful',
                                     u'Program [{0}] successful deleted!'.format(name))
