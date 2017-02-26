# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>

program_page_files.py: Program Wizard Files Page

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

import os
import posixpath
import sys

from PyQt4.QtCore import Qt, QDir
from PyQt4.QtGui import QIcon, QListWidgetItem, QApplication

from brickv.plugin_system.plugins.red.program_page import ProgramPage
from brickv.plugin_system.plugins.red.program_utils import *
from brickv.plugin_system.plugins.red.ui_program_page_files import Ui_ProgramPageFiles
from brickv.utils import get_main_window, get_home_path, get_open_file_names, \
                         get_existing_directory
from brickv.load_pixmap import load_pixmap

class ProgramPageFiles(ProgramPage, Ui_ProgramPageFiles):
    def __init__(self, title_prefix='', last_directory=None):
        ProgramPage.__init__(self)

        self.setupUi(self)

        self.edit_mode   = False
        self.folder_icon = QIcon(load_pixmap('folder-icon.png'))
        self.file_icon   = QIcon(load_pixmap('file-icon.png'))

        if last_directory != None:
            self.last_directory = last_directory
        else:
            self.last_directory = get_home_path()

        self.setTitle(title_prefix + 'Files')

        self.list_files.itemSelectionChanged.connect(self.update_ui_state)
        self.button_add_files.clicked.connect(self.show_add_files_dialog)
        self.button_add_directory.clicked.connect(self.show_add_directory_dialog)
        self.button_remove_selected_files.clicked.connect(self.remove_selected_files)

    # overrides QWizardPage.initializePage
    def initializePage(self):
        self.set_formatted_sub_title(u'Specify the files to be uploaded for the {language} program [{name}].')
        self.list_files.clear()
        self.update_ui_state()

        # if a program exists then this page is used in an edit wizard
        if self.wizard().program != None:
            self.edit_mode = True

    # overrides QWizardPage.isComplete
    def isComplete(self):
        if self.edit_mode:
            return self.list_files.count() > 0 and ProgramPage.isComplete(self)

        return ProgramPage.isComplete(self)

    # overrides ProgramPage.update_ui_state
    def update_ui_state(self):
        self.button_remove_selected_files.setEnabled(len(self.list_files.selectedItems()) > 0)

    def show_add_files_dialog(self):
        filenames = get_open_file_names(get_main_window(), 'Add Files', self.last_directory)

        if len(filenames) > 0:
            self.last_directory = os.path.split(filenames[0])[0]

        for filename in filenames:
            if len(self.list_files.findItems(filename, Qt.MatchFixedString)) > 0:
                continue

            uploads = [Upload(filename, os.path.split(filename)[1])]

            item = QListWidgetItem(filename)
            item.setData(Qt.UserRole, uploads)
            item.setData(Qt.DecorationRole, self.file_icon)
            self.list_files.addItem(item)

        self.completeChanged.emit()

    def show_add_directory_dialog(self):
        directory = get_existing_directory(get_main_window(), 'Add Directory', self.last_directory)

        if len(directory) == 0:
            return

        self.last_directory = directory

        if len(self.list_files.findItems(os.path.join(directory, '*'), Qt.MatchFixedString)) > 0:
            return

        uploads = []

        progress = ExpandingProgressDialog(self)
        progress.set_progress_text_visible(False)
        progress.setWindowTitle('New Program')
        progress.setLabelText(u"Collecting content of {0}".format(directory))
        progress.setModal(True)
        progress.setRange(0, 0)
        progress.show()

        for root, directories, files in os.walk(directory):
            if progress.wasCanceled():
                break

            for filename in files:
                source = os.path.join(root, filename)
                target = QDir.fromNativeSeparators(os.path.relpath(source, directory))
                uploads.append(Upload(source, target))

                # ensure that the UI stays responsive
                QApplication.processEvents()

                if progress.wasCanceled():
                    break

        if progress.wasCanceled():
            return

        progress.cancel()

        # FIXME: maybe add a warning if the directory contains very many files or large amounts of data

        item = QListWidgetItem(os.path.join(directory, '*'))
        item.setData(Qt.UserRole, uploads)
        item.setData(Qt.DecorationRole, self.folder_icon)
        self.list_files.addItem(item)

        self.completeChanged.emit()

    def remove_selected_files(self):
        for item in self.list_files.selectedItems():
            self.list_files.takeItem(self.list_files.row(item))

        self.completeChanged.emit()

    def get_items(self):
        items = []

        for row in range(self.list_files.count()):
            items.append(self.list_files.item(row).text())

        return items

    def get_directories(self):
        directories = set()

        for upload in self.get_uploads():
            directory = os.path.split(upload.target)[0]

            if len(directory) > 0:
                directories.add(directory)

        return sorted(list(directories))

    def get_uploads(self):
        uploads = []

        for row in range(self.list_files.count()):
            uploads += self.list_files.item(row).data(Qt.UserRole)

        return uploads
