# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_general.py: New Program Wizard General Page

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

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QWizardPage, QRegExpValidator
from brickv.plugin_system.plugins.red.new_program_pages import *
from brickv.plugin_system.plugins.red.ui_new_program_general import Ui_NewProgramGeneral

class NewProgramGeneral(QWizardPage, Ui_NewProgramGeneral):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('General Information')
        self.setSubTitle('Specify an identifier and select a programming language for the new program.')

        self.edit_identifier.setValidator(QRegExpValidator(QRegExp('^[a-zA-Z0-9._][a-zA-Z0-9._-]{2,}$'), self))

        self.registerField('identifier*', self.edit_identifier)
        self.registerField('language', self.combo_language, 'currentText')

    # overrides QWizardPage.nextId
    def nextId(self):
        return PAGE_FILES
