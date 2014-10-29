# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_page.py: Program Wizard Page

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
from brickv.plugin_system.plugins.red.program_wizard_utils import *

class ProgramPage(QWizardPage):
    # makes QWizardPage.field virtual
    def get_field(self, name):
        return self.wizard().get_field(name)

    def set_formatted_sub_title(self, sub_title):
        language = Constants.language_display_names[self.get_field('language').toInt()[0]]
        name     = unicode(Qt.escape(self.get_field('name').toString()))

        self.setSubTitle(sub_title.format(**{'language': language, 'name': name}))
