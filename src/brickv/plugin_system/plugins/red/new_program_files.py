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

from PyQt4.QtCore import QDir
from PyQt4.QtGui import QWizardPage, QFileDialog
from brickv.plugin_system.plugins.red.new_program_pages import *
from brickv.plugin_system.plugins.red.ui_new_program_files import Ui_NewProgramFiles
import os

class NewProgramFiles(QWizardPage, Ui_NewProgramFiles):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Program Files')

        self.list_files.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_files.clicked.connect(self.show_add_files_dialog)
        self.button_add_directory.clicked.connect(self.show_add_directory_dialog)
        self.button_remove.clicked.connect(self.remove_selected_files)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle('Specify the files to be uploaded for the new {0} program [{1}].'.format(str(self.field('language').toString()),
                                                                                                  str(self.field('name').toString())))
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

    def show_add_files_dialog(self):
        filenames = QFileDialog.getOpenFileNames(self, "Select files to be uploaded")

        for filename in filenames:
            self.list_files.addItem(QDir.toNativeSeparators(filename))

    def show_add_directory_dialog(self):
        directory = unicode(QDir.toNativeSeparators(QFileDialog.getExistingDirectory(self, "Select a directory of files to be uploaded")))

        if len(directory) > 0:
            self.list_files.addItem(os.path.join(directory, '*'))

    def remove_selected_files(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))
