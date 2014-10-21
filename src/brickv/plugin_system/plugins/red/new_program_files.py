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

from PyQt4.QtCore import Qt, QDir, QVariant
from PyQt4.QtGui import QWizardPage, QFileDialog, QListWidgetItem, QProgressDialog, QApplication
from brickv.plugin_system.plugins.red.new_program_utils import Constants
from brickv.plugin_system.plugins.red.ui_new_program_files import Ui_NewProgramFiles
import os
from collections import namedtuple

Upload = namedtuple('Upload', ['source', 'target'])

class NewProgramFiles(QWizardPage, Ui_NewProgramFiles):
    def __init__(self, *args, **kwargs):
        QWizardPage.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.setTitle('Step 2 of {0}: Files'.format(Constants.STEP_COUNT))

        self.list_files.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_files.clicked.connect(self.show_add_files_dialog)
        self.button_add_directory.clicked.connect(self.show_add_directory_dialog)
        self.button_remove_selected_files.clicked.connect(self.remove_selected_files)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.setSubTitle(u'Specify the files to be uploaded for the new {0} program [{1}].'
                         .format(Constants.language_names[self.field('language').toInt()[0]],
                                 unicode(self.field('name').toString())))
        self.list_files.clear()
        self.update_ui_state()

    # overrides QWizardPage.nextId
    def nextId(self):
        language = self.field('language').toInt()[0]

        if language == Constants.LANGUAGE_JAVA:
            return Constants.PAGE_JAVA
        elif language == Constants.LANGUAGE_PYTHON:
            return Constants.PAGE_PYTHON
        else:
            return Constants.PAGE_GENERAL

    def update_ui_state(self):
        self.button_remove_selected_files.setEnabled(len(self.list_files.selectedItems()) > 0)

    def show_add_files_dialog(self):
        filenames = QFileDialog.getOpenFileNames(self, "Select files to be uploaded")

        for filename in filenames:
            filename = unicode(QDir.toNativeSeparators(filename))

            if len(self.list_files.findItems(filename, Qt.MatchFixedString)) > 0:
                continue

            uploads = [Upload(filename, os.path.split(filename)[1])]

            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, QVariant(uploads))
            self.list_files.addItem(item)

    def show_add_directory_dialog(self):
        directory = unicode(QDir.toNativeSeparators(QFileDialog.getExistingDirectory(self, "Select a directory of files to be uploaded")))

        if len(directory) == 0:
            return

        if len(self.list_files.findItems(os.path.join(directory, '*'), Qt.MatchFixedString)) > 0:
            return

        uploads = []
        progress = QProgressDialog(self)
        progress.setWindowTitle('New Program')
        progress.setLabelText(u"Collecting content of '{0}'".format(directory))
        progress.setWindowModality(Qt.WindowModal)
        progress.setMaximum(0)
        progress.setValue(0)
        progress.show()

        for root, directories, files in os.walk(directory):
            for filename in files:
                source = os.path.join(root, filename)
                target = os.path.relpath(source, directory)
                uploads.append(Upload(source, target))

                QApplication.processEvents()

                if progress.wasCanceled():
                    break

        if progress.wasCanceled():
            return

        progress.cancel()

        # FIXME: maybe add a warning if the directory contains very many files or a large amount of data

        item = QListWidgetItem(os.path.join(directory, '*'))
        item.setData(Qt.UserRole, QVariant(uploads))
        self.list_files.addItem(item)

    def remove_selected_files(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))

    def get_items(self):
        items = []

        for row in range(self.list_files.count()):
            items.append(self.list_files.item(row).text())

        return items

    def get_uploads(self):
        uploads = []

        for row in range(self.list_files.count()):
            uploads += self.list_files.item(row).data(Qt.UserRole).toPyObject()

        return uploads
