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

from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_program import Ui_REDTabProgram
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.new_program import NewProgram

class REDTabProgram(QtGui.QWidget, Ui_REDTabProgram):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None
        self.defined_programs = []
        self.identifiers = []
        self.new_program_wizard = None

        self.button_new.clicked.connect(self.show_new_program_wizard)

    def tab_on_focus(self):
        self.defined_programs = get_defined_programs(self.session)
        self.identifiers = []

        self.list_programs.clear()

        for program in self.defined_programs.items:
            self.identifiers.append(str(program.identifier))

            self.list_programs.addItem(str(program.identifier))

    def tab_off_focus(self):
        pass

    def show_new_program_wizard(self):
        self.new_program_wizard = NewProgram(self.identifiers)
        self.new_program_wizard.show()
