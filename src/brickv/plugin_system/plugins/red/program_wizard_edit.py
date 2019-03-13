# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

program_wizard_edit.py: Edit Program Wizard

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

from brickv.plugin_system.plugins.red.program_wizard import ProgramWizard
from brickv.plugin_system.plugins.red.program_utils import *

class ProgramWizardEdit(ProgramWizard):
    def __init__(self, parent, context, program, available_files, available_directories):
        super().__init__(self, parent, context)

        self.program               = program
        self.available_files       = available_files
        self.available_directories = available_directories

        self.setWindowTitle('Edit Program')

    # overrides QWizard.nextId
    def nextId(self):
        return -1

    # overrides ProgramWizard.get_field
    def get_field(self, name):
        if self.currentId() == Constants.PAGE_GENERAL:
            return ProgramWizard.get_field(self, name)
        elif name == 'identifier':
            return self.program.identifier
        elif name == 'name':
            return self.program.cast_custom_option_value('name', str, '<unknown>')
        elif name == 'language':
            language_api_name = self.program.cast_custom_option_value('language', str, '<unknown>')

            try:
                return Constants.get_language(language_api_name)
            except:
                return Constants.LANGUAGE_INVALID
        else:
            return ProgramWizard.get_field(self, name)
