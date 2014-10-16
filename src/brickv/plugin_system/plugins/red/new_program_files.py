# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

new_program_files.py: New Program Wizard Files Page

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
from brickv.plugin_system.plugins.red.new_program_pages import *
from brickv.plugin_system.plugins.red.ui_new_program_files import Ui_NewProgramFiles

class NewProgramFiles(QWizardPage, Ui_NewProgramFiles):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Program Files')

        self.list_files.itemSelectionChanged.connect(self.update_ui_state)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify the files to be uploaded for the new {0} program [{1}].'.format(str(self.field('language').toString()),
                                                                                                  str(self.field('identifier').toString())))
        self.list_files.clear()
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        language = str(self.field('language').toString())

        if language == 'Java':
            return PAGE_JAVA
        elif language == 'Python':
            return PAGE_PYTHON
        else:
            return PAGE_GENERAL

    def update_ui_state(self):
        self.button_remove.setEnabled(len(self.list_files.selectedItems()) > 0)
