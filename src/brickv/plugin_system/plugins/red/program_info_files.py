# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

program_info_files.py: Program Files Info Widget

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

from PyQt4.QtCore import Qt, QDateTime, QVariant
from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem, QSortFilterProxyModel
from brickv.plugin_system.plugins.red.ui_program_info_files import Ui_ProgramInfoFiles
from brickv.async_call import async_call
import os
import json

def expand_directory_walk_to_lists(directory_walk):
    files = []
    directories = set()

    def expand(root, dw):
        if 'c' in dw:
            if len(root) > 0:
                directories.add(root)

            for child_name, child_dw in dw['c'].iteritems():
                expand(os.path.join(root, child_name), child_dw)
        else:
            files.append(root)

    expand('', directory_walk)

    return sorted(files), sorted(list(directories))


def get_file_display_size(size):
    if size < 1024:
        return str(size) + ' Bytes'
    else:
        return str(size / 1024) + ' kiB'


def expand_directory_walk_to_model(directory_walk, model):
    def create_last_modified_item(last_modified):
        item = QStandardItem(QDateTime.fromTime_t(last_modified).toString('yyyy-MM-dd HH:mm:ss'))
        item.setData(QVariant(last_modified))

        return item

    def expand(parent_item, name, dw):
        if 'c' in dw:
            if name == None:
                name_item = parent_item
                size_item = None
            else:
                name_item          = QStandardItem(name)
                size_item          = QStandardItem('')
                last_modified_item = create_last_modified_item(int(dw['l']))

                parent_item.appendRow([name_item, size_item, last_modified_item])

            size = 0

            for child_name, child_dw in dw['c'].iteritems():
                size += expand(name_item, child_name, child_dw)

            if size_item != None:
                size_item.setText(get_file_display_size(size))
                size_item.setData(QVariant(size))

            return size
        else:
            size      = int(dw['s'])
            size_item = QStandardItem(get_file_display_size(size))
            size_item.setData(QVariant(size))

            last_modified_item = create_last_modified_item(int(dw['l']))

            parent_item.appendRow([QStandardItem(name), size_item, last_modified_item])

            return size

    expand(model.invisibleRootItem(), None, directory_walk)

    return model


class FilesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        # size and last modified
        if left.column() in [1, 2]:
            return left.data(Qt.UserRole + 1).toInt()[0] < right.data(Qt.UserRole + 1).toInt()[0]

        return QSortFilterProxyModel.lessThan(self, left, right)


class ProgramInfoFiles(QWidget, Ui_ProgramInfoFiles):
    def __init__(self, context, update_main_ui_state, set_widget_enabled, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.script_manager          = context.script_manager
        self.program                 = context.program
        self.update_main_ui_state    = update_main_ui_state
        self.set_widget_enabled      = set_widget_enabled
        self.bin_directory           = os.path.join(unicode(self.program.root_directory), 'bin')
        self.refresh_in_progress     = False
        self.available_files         = []
        self.available_directories   = []
        self.tree_files_model        = QStandardItemModel(self)
        self.tree_files_model_header = ['Name', 'Size', 'Last Modified']
        self.tree_files_proxy_model  = FilesProxyModel(self)

        self.tree_files_model.setHorizontalHeaderLabels(self.tree_files_model_header)
        self.tree_files_proxy_model.setSourceModel(self.tree_files_model)
        self.tree_files.setModel(self.tree_files_model)
        self.tree_files.setModel(self.tree_files_proxy_model)
        self.tree_files.setColumnWidth(0, 210)
        self.tree_files.setColumnWidth(1, 85)

        self.tree_files.selectionModel().selectionChanged.connect(self.update_ui_state)
        self.button_upload_files.clicked.connect(self.upload_files)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)

    def update_ui_state(self):
        selection_count = len(self.tree_files.selectionModel().selectedRows())

        self.set_widget_enabled(self.button_download_files, selection_count > 0)
        self.set_widget_enabled(self.button_rename_file, selection_count == 1)
        self.set_widget_enabled(self.button_delete_files, selection_count > 0)

    def refresh_files(self):
        def cb_directory_walk(result):
            if result == None or len(result.stderr) > 0:
                self.refresh_in_progress = False
                self.update_main_ui_state()
                return # FIXME: report error

            def expand_async(data):
                directory_walk        = json.loads(data)
                available_files       = []
                available_directories = []

                if directory_walk != None:
                    available_files, available_directories = expand_directory_walk_to_lists(directory_walk)

                return directory_walk, available_files, available_directories

            def cb_expand_success(args):
                directory_walk, available_files, available_directories = args

                self.available_files       = available_files
                self.available_directories = available_directories
                self.refresh_in_progress   = False
                self.update_main_ui_state()

                expand_directory_walk_to_model(directory_walk, self.tree_files_model)

                self.tree_files.header().setSortIndicator(0, Qt.AscendingOrder)

            def cb_expand_error():
                pass # FIXME: report error

            async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

        self.refresh_in_progress = True
        self.update_main_ui_state()

        width1 = self.tree_files.columnWidth(0)
        width2 = self.tree_files.columnWidth(1)

        self.tree_files_model.clear()
        self.tree_files_model.setHorizontalHeaderLabels(self.tree_files_model_header)
        self.tree_files.setColumnWidth(0, width1)
        self.tree_files.setColumnWidth(1, width2)

        self.script_manager.execute_script('directory_walk', cb_directory_walk,
                                           [self.bin_directory], max_len=1024*1024)

    def upload_files(self):
        print 'upload_files'

    def download_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'download_selected_files', filenames

    def rename_selected_file(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filename = unicode(selected_items[0].text())

        print 'rename_selected_file', filename

    def delete_selected_files(self):
        selected_items = self.tree_files.selectedItems()

        if len(selected_items) == 0:
            return

        filenames = [unicode(selected_item.text()) for selected_item in selected_items]

        print 'delete_selected_files', filenames
