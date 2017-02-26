# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

program_wizard.py: Program Wizard

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

from collections import namedtuple

from PyQt4.QtGui import QWizard

ProgramWizardContext = namedtuple('ProgramWizardContext', 'session identifiers script_manager image_version executable_versions')

class ProgramWizard(QWizard):
    def __init__(self, parent, context):
        QWizard.__init__(self, parent)

        self.setModal(True)

        self.session             = context.session
        self.identifiers         = context.identifiers
        self.script_manager      = context.script_manager
        self.image_version       = context.image_version
        self.executable_versions = context.executable_versions

    # overrides QWizard.sizeHint
    def sizeHint(self):
        size = QWizard.sizeHint(self)

        if size.width() < 700:
            size.setWidth(700)

        if size.height() < 700:
            size.setHeight(700)

        return size

    # makes QWizard.field virtual
    def get_field(self, name):
        return QWizard.field(self, name)
