# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2017 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

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

import os
import posixpath
import json
import zlib
import sys
import html

from PyQt5.QtCore import Qt, QDateTime, QDir, QSortFilterProxyModel
from PyQt5.QtWidgets import QWidget, QDialog, QMessageBox, QInputDialog, QApplication
from PyQt5.QtGui import QStandardItem, QStandardItemModel, QIcon

from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import Download, ExpandingProgressDialog, \
                                                           ExpandingInputDialog, get_file_display_size
from brickv.plugin_system.plugins.red.ui_program_info_files import Ui_ProgramInfoFiles
from brickv.plugin_system.plugins.red.program_info_files_permissions import ProgramInfoFilesPermissions
from brickv.plugin_system.plugins.red.script_manager import check_script_result, report_script_result
from brickv.async_call import async_call
from brickv.utils import get_main_window, get_home_path, get_existing_directory
from brickv.load_pixmap import load_pixmap

USER_ROLE_ITEM_TYPE     = Qt.UserRole + 2
USER_ROLE_SIZE          = Qt.UserRole + 3
USER_ROLE_LAST_MODIFIED = Qt.UserRole + 4
USER_ROLE_PERMISSIONS   = Qt.UserRole + 5

ITEM_TYPE_FILE      = 1
ITEM_TYPE_DIRECTORY = 2


def expand_walk_to_lists(walk):
    files       = []
    directories = set()

    def expand(root, dw):
        if 'c' in dw:
            if len(root) > 0:
                directories.add(root)

            for child_name, child_dw in dw['c'].items():
                expand(posixpath.join(root, child_name), child_dw)
        else:
            files.append(root)

    expand('', walk)

    return sorted(files), sorted(list(directories))


def get_full_item_path(item):
    def expand(item, path):
        parent = item.parent()

        if parent != None:
            return expand(parent, posixpath.join(parent.text(), path))
        else:
            return path

    return expand(item, item.text())


def expand_walk_to_model(walk, model, folder_icon, file_icon):
    def create_last_modified_item(last_modified):
        item = QStandardItem(QDateTime.fromTime_t(last_modified).toString('yyyy-MM-dd HH:mm:ss'))
        item.setData(last_modified, USER_ROLE_LAST_MODIFIED)

        return item

    def expand(parent_item, name, dw):
        QApplication.processEvents()

        if 'c' in dw:
            if name == None:
                name_item = parent_item
                size_item = None
            else:
                name_item = QStandardItem(name)
                name_item.setData(folder_icon, Qt.DecorationRole)
                name_item.setData(ITEM_TYPE_DIRECTORY, USER_ROLE_ITEM_TYPE)
                name_item.setData(int(dw['p']), USER_ROLE_PERMISSIONS)

                size_item          = QStandardItem('')
                last_modified_item = create_last_modified_item(int(dw['l']))

                parent_item.appendRow([name_item, size_item, last_modified_item])

            size = 0

            for child_name, child_dw in dw['c'].items():
                size += expand(name_item, child_name, child_dw)

            if size_item != None:
                size_item.setText(get_file_display_size(size))
                size_item.setData(size, USER_ROLE_SIZE)

            return size
        else:
            name_item = QStandardItem(name)
            name_item.setData(file_icon, Qt.DecorationRole)
            name_item.setData(ITEM_TYPE_FILE, USER_ROLE_ITEM_TYPE)
            name_item.setData(int(dw['p']), USER_ROLE_PERMISSIONS)

            size      = int(dw['s'])
            size_item = QStandardItem(get_file_display_size(size))
            size_item.setData(size, USER_ROLE_SIZE)

            last_modified_item = create_last_modified_item(int(dw['l']))

            parent_item.appendRow([name_item, size_item, last_modified_item])

            return size

    expand(model.invisibleRootItem(), None, walk)

    return model


class FilesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        if left.column() == 1: # size
            return left.data(USER_ROLE_SIZE) < right.data(USER_ROLE_SIZE)
        elif left.column() == 2: # last modified
            return left.data(USER_ROLE_LAST_MODIFIED) < right.data(USER_ROLE_LAST_MODIFIED)

        return QSortFilterProxyModel.lessThan(self, left, right)


class ProgramInfoFiles(QWidget, Ui_ProgramInfoFiles):
    def __init__(self, context, update_main_ui_state, set_widget_enabled, is_alive, show_upload_files_wizard, show_download_wizard):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session                 = context.session
        self.script_manager          = context.script_manager
        self.program                 = context.program
        self.update_main_ui_state    = update_main_ui_state
        self.set_widget_enabled      = set_widget_enabled
        self.is_alive                = is_alive
        self.show_download_wizard    = show_download_wizard
        self.bin_directory           = posixpath.join(self.program.root_directory, 'bin')
        self.refresh_in_progress     = False
        self.any_refresh_in_progress = False # set from ProgramInfoMain.update_ui_state
        self.available_files         = []
        self.available_directories   = []
        self.folder_icon             = QIcon(load_pixmap('folder-icon.png'))
        self.file_icon               = QIcon(load_pixmap('file-icon.png'))
        self.tree_files_model        = QStandardItemModel(self)
        self.tree_files_model_header = ['Name', 'Size', 'Last Modified']
        self.tree_files_proxy_model  = FilesProxyModel(self)
        self.last_download_directory = get_home_path()

        self.tree_files_model.setHorizontalHeaderLabels(self.tree_files_model_header)
        self.tree_files_proxy_model.setSourceModel(self.tree_files_model)
        self.tree_files.setModel(self.tree_files_model)
        self.tree_files.setModel(self.tree_files_proxy_model)
        self.tree_files.setColumnWidth(0, 210)
        self.tree_files.setColumnWidth(1, 85)

        self.tree_files.selectionModel().selectionChanged.connect(self.update_ui_state)
        self.tree_files.activated.connect(self.rename_activated_file)
        self.button_upload_files.clicked.connect(show_upload_files_wizard)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_change_file_permissions.clicked.connect(self.change_permissions_of_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)

        self.label_error.setVisible(False)

    def update_ui_state(self):
        selection_count = len(self.tree_files.selectionModel().selectedRows())

        self.set_widget_enabled(self.button_upload_files, not self.any_refresh_in_progress)
        self.set_widget_enabled(self.button_download_files, not self.any_refresh_in_progress and selection_count > 0)
        self.set_widget_enabled(self.button_rename_file, not self.any_refresh_in_progress and selection_count == 1)
        self.set_widget_enabled(self.button_change_file_permissions, not self.any_refresh_in_progress and selection_count == 1)
        self.set_widget_enabled(self.button_delete_files, not self.any_refresh_in_progress and selection_count > 0)

    def close_all_dialogs(self):
        pass

    def refresh_files_done(self):
        self.refresh_in_progress = False
        self.update_main_ui_state()

    def refresh_files(self):
        def cb_walk(result):
            okay, message = check_script_result(result, decode_stderr=True)

            if not okay:
                self.label_error.setText('<b>Error:</b> ' + html.escape(message))
                self.label_error.setVisible(True)
                self.refresh_files_done()
                return

            self.label_error.setVisible(False)

            def expand_async(data):
                try:
                    walk = json.loads(zlib.decompress(memoryview(data)).decode('utf-8'))
                except:
                    walk = None

                if walk == None or not isinstance(walk, dict):
                    available_files       = []
                    available_directories = []
                    walk                  = None
                else:
                    available_files, available_directories = expand_walk_to_lists(walk)

                return walk, available_files, available_directories

            def cb_expand_success(result):
                walk, available_files, available_directories = result

                self.available_files       = available_files
                self.available_directories = available_directories

                if walk != None:
                    expand_walk_to_model(walk, self.tree_files_model, self.folder_icon, self.file_icon)
                else:
                    self.label_error.setText('<b>Error:</b> Received invalid data')
                    self.label_error.setVisible(True)

                self.tree_files.header().setSortIndicator(0, Qt.AscendingOrder)
                self.refresh_files_done()

            def cb_expand_error():
                self.label_error.setText('<b>Error:</b> Internal async error')
                self.label_error.setVisible(True)
                self.refresh_files_done()

            async_call(expand_async, result.stdout, cb_expand_success, cb_expand_error)

        self.refresh_in_progress = True
        self.update_main_ui_state()

        width1 = self.tree_files.columnWidth(0)
        width2 = self.tree_files.columnWidth(1)

        self.tree_files_model.clear()
        self.tree_files_model.setHorizontalHeaderLabels(self.tree_files_model_header)
        self.tree_files.setColumnWidth(0, width1)
        self.tree_files.setColumnWidth(1, width2)

        self.script_manager.execute_script('walk', cb_walk,
                                           [self.bin_directory], max_length=1024*1024,
                                           decode_output_as_utf8=False)

    def get_directly_selected_name_items(self):
        selected_indexes    = self.tree_files.selectedIndexes()
        selected_name_items = []

        for selected_index in selected_indexes:
            if selected_index.column() == 0:
                mapped_index = self.tree_files_proxy_model.mapToSource(selected_index)
                selected_name_items.append(self.tree_files_model.itemFromIndex(mapped_index))

        return selected_name_items

    def download_selected_files(self):
        selected_name_items = self.get_directly_selected_name_items()

        if len(selected_name_items) == 0:
            return

        downloads = []

        def expand(name_item):
            item_type = name_item.data(USER_ROLE_ITEM_TYPE)

            if item_type == ITEM_TYPE_DIRECTORY:
                for i in range(name_item.rowCount()):
                    expand(name_item.child(i, 0))
            elif item_type == ITEM_TYPE_FILE:
                filename = get_full_item_path(name_item)

                downloads.append(Download(filename, QDir.toNativeSeparators(filename)))

        for selected_name_item in selected_name_items:
            expand(selected_name_item)

        if len(downloads) == 0:
            return

        download_directory = get_existing_directory(get_main_window(), 'Download Files',
                                                    self.last_download_directory)

        if len(download_directory) == 0:
            return

        self.last_download_directory = download_directory

        self.show_download_wizard('files', download_directory, downloads)

    def rename_activated_file(self, index):
        if index.column() == 0 and not self.any_refresh_in_progress:
            mapped_index = self.tree_files_proxy_model.mapToSource(index)
            name_item    = self.tree_files_model.itemFromIndex(mapped_index)
            item_type    = name_item.data(USER_ROLE_ITEM_TYPE)

            # only rename files via activation, because directories are expanded
            if item_type == ITEM_TYPE_FILE:
                self.rename_item(name_item)

    def rename_selected_file(self):
        selection_count = len(self.tree_files.selectionModel().selectedRows())

        if selection_count != 1:
            return

        selected_name_items = self.get_directly_selected_name_items()

        if len(selected_name_items) != 1:
            return

        self.rename_item(selected_name_items[0])

    def rename_item(self, name_item):
        item_type = name_item.data(USER_ROLE_ITEM_TYPE)

        if item_type == ITEM_TYPE_FILE:
            title     = 'Rename File'
            type_name = 'file'
        else:
            title     = 'Rename Directory'
            type_name = 'directory'

        old_name = name_item.text()

        # get new name
        dialog = ExpandingInputDialog(get_main_window())
        dialog.setModal(True)
        dialog.setWindowTitle(title)
        dialog.setLabelText('Enter new {0} name:'.format(type_name))
        dialog.setInputMode(QInputDialog.TextInput)
        dialog.setTextValue(old_name)
        dialog.setOkButtonText('Rename')

        if dialog.exec_() != QDialog.Accepted:
            return

        new_name = dialog.textValue()

        if new_name == old_name:
            return

        # check that new name is valid
        if len(new_name) == 0 or new_name == '.' or new_name == '..' or '/' in new_name:
            QMessageBox.critical(get_main_window(), title + ' Error',
                                 'A {0} name cannot be empty, cannot be one dot [.], cannot be two dots [..] and cannot contain a forward slash [/].'
                                 .format(type_name))
            return

        # check that new name is not already in use
        name_item_parent = name_item.parent()

        if name_item_parent == None:
            name_item_parent = self.tree_files_model.invisibleRootItem()

        for i in range(name_item_parent.rowCount()):
            if new_name == name_item_parent.child(i).text():
                QMessageBox.critical(get_main_window(), title + ' Error',
                                     'The new {0} name is already in use.'.format(type_name))
                return

        absolute_old_name = posixpath.join(self.bin_directory, get_full_item_path(name_item))
        absolute_new_name = posixpath.join(posixpath.split(absolute_old_name)[0], new_name)

        def cb_rename(result):
            if not report_script_result(result, title + ' Error', 'Could not rename {0}'.format(type_name)):
                return

            name_item.setText(new_name)

            if self.tree_files.header().sortIndicatorSection() == 0:
                self.tree_files.header().setSortIndicator(0, self.tree_files.header().sortIndicatorOrder())

        self.script_manager.execute_script('rename', cb_rename,
                                           [absolute_old_name, absolute_new_name])

    def change_permissions_of_selected_file(self):
        selection_count = len(self.tree_files.selectionModel().selectedRows())

        if selection_count != 1:
            return

        selected_name_items = self.get_directly_selected_name_items()

        if len(selected_name_items) != 1:
            return

        name_item = selected_name_items[0]
        item_type = name_item.data(USER_ROLE_ITEM_TYPE)
        old_permissions = name_item.data(USER_ROLE_PERMISSIONS)

        if item_type == ITEM_TYPE_FILE:
            title     = 'Change File Permissions'
            type_name = 'file'
        else:
            title     = 'Change Directory Permissions'
            type_name = 'directory'

        dialog = ProgramInfoFilesPermissions(get_main_window(), title, old_permissions)

        if dialog.exec_() != QDialog.Accepted:
            return

        new_permissions = dialog.get_permissions()

        if new_permissions == (old_permissions & 0o777):
            return

        absolute_name = posixpath.join(self.bin_directory, get_full_item_path(name_item))

        def cb_change_permissions(result):
            if not report_script_result(result, title + ' Error', 'Could change {0} permissions'.format(type_name)):
                return

            name_item.setData(new_permissions, USER_ROLE_PERMISSIONS)

        self.script_manager.execute_script('change_permissions', cb_change_permissions,
                                           [absolute_name, str(new_permissions)])

    def delete_selected_files(self):
        button = QMessageBox.question(get_main_window(), 'Delete Files',
                                      'Irreversibly deleting selected files and directories.',
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if not self.is_alive() or button != QMessageBox.Ok:
            return

        selected_name_items = self.get_directly_selected_name_items()

        if len(selected_name_items) == 0:
            return

        script_instance_ref = [None]

        def progress_canceled():
            script_instance = script_instance_ref[0]

            if script_instance == None:
                return

            self.script_manager.abort_script(script_instance)

        progress = ExpandingProgressDialog(self)
        progress.set_progress_text_visible(False)
        progress.setModal(True)
        progress.setWindowTitle('Delete Files')
        progress.setLabelText('Collecting files and directories to delete')
        progress.setRange(0, 0)
        progress.canceled.connect(progress_canceled)
        progress.show()

        files_to_delete = []
        dirs_to_delete  = []
        all_done        = False

        while not all_done:
            all_done = True

            for selected_name_item in list(selected_name_items):
                item_done = False
                parent = selected_name_item.parent()

                while not item_done and parent != None:
                    if parent in selected_name_items:
                        selected_name_items.remove(selected_name_item)
                        item_done = True
                    else:
                        parent = parent.parent()

                if item_done:
                    all_done = False
                    break

        for selected_name_item in selected_name_items:
            path      = get_full_item_path(selected_name_item)
            item_type = selected_name_item.data(USER_ROLE_ITEM_TYPE)

            if item_type == ITEM_TYPE_DIRECTORY:
                dirs_to_delete.append(posixpath.join(self.bin_directory, path))
            else:
                files_to_delete.append(posixpath.join(self.bin_directory, path))

        message = 'Deleting '

        if len(files_to_delete) == 1:
            message += '1 file '
        elif len(files_to_delete) > 1:
            message += '{0} files '.format(len(files_to_delete))

        if len(dirs_to_delete) == 1:
            if len(files_to_delete) > 0:
                message += 'and '

            message += '1 directory'
        elif len(dirs_to_delete) > 1:
            if len(files_to_delete) > 0:
                message += 'and '

            message += '{0} directories'.format(len(dirs_to_delete))

        progress.setLabelText(message)

        def cb_delete(result):
            script_instance = script_instance_ref[0]

            if script_instance != None:
                aborted = script_instance.abort
            else:
                aborted = False

            script_instance_ref[0] = None

            progress.cancel()
            self.refresh_files()

            if aborted:
                QMessageBox.information(get_main_window(), 'Delete Files',
                                        'Delete operation was aborted.')
                return

            report_script_result(result, 'Delete Files Error', 'Could not delete selected files/directories:')

        script_instance_ref[0] = self.script_manager.execute_script('delete', cb_delete,
                                                                    [json.dumps(files_to_delete), json.dumps(dirs_to_delete)],
                                                                    execute_as_user=True)
