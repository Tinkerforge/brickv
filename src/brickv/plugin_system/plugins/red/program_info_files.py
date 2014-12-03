# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
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

from PyQt4.QtCore import Qt, QDateTime, QVariant, QDir
from PyQt4.QtGui import QIcon, QWidget, QStandardItemModel, QStandardItem, \
                        QAbstractItemView, QLineEdit, QSortFilterProxyModel, \
                        QFileDialog, QMessageBox, QInputDialog, QApplication, QDialog
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import Download, ExpandingProgressDialog, \
                                                           ExpandingInputDialog, get_file_display_size
from brickv.plugin_system.plugins.red.ui_program_info_files import Ui_ProgramInfoFiles
from brickv.async_call import async_call
from brickv.utils import get_main_window, get_resources_path
import os
import posixpath
import json
import zlib
import sys

USER_ROLE_ITEM_TYPE     = Qt.UserRole + 2
USER_ROLE_SIZE          = Qt.UserRole + 3
USER_ROLE_LAST_MODIFIED = Qt.UserRole + 4

ITEM_TYPE_FILE      = 1
ITEM_TYPE_DIRECTORY = 2


def expand_directory_walk_to_lists(directory_walk):
    files       = []
    directories = set()

    def expand(root, dw):
        if 'c' in dw:
            if len(root) > 0:
                directories.add(root)

            for child_name, child_dw in dw['c'].iteritems():
                expand(posixpath.join(root, child_name), child_dw)
        else:
            files.append(root)

    expand('', directory_walk)

    return sorted(files), sorted(list(directories))


def get_full_item_path(item):
    def expand(item, path):
        parent = item.parent()

        if parent != None:
            return expand(parent, posixpath.join(unicode(parent.text()), path))
        else:
            return path

    return expand(item, unicode(item.text()))


def expand_directory_walk_to_model(directory_walk, model, folder_icon, file_icon):
    def create_last_modified_item(last_modified):
        item = QStandardItem(QDateTime.fromTime_t(last_modified).toString('yyyy-MM-dd HH:mm:ss'))
        item.setData(QVariant(last_modified), USER_ROLE_LAST_MODIFIED)

        return item

    def expand(parent_item, name, dw):
        QApplication.processEvents()

        if 'c' in dw:
            if name == None:
                name_item = parent_item
                size_item = None
            else:
                name_item = QStandardItem(name)
                name_item.setData(QVariant(folder_icon), Qt.DecorationRole)
                name_item.setData(QVariant(ITEM_TYPE_DIRECTORY), USER_ROLE_ITEM_TYPE)

                size_item          = QStandardItem('')
                last_modified_item = create_last_modified_item(int(dw['l']))

                parent_item.appendRow([name_item, size_item, last_modified_item])

            size = 0

            for child_name, child_dw in dw['c'].iteritems():
                size += expand(name_item, child_name, child_dw)

            if size_item != None:
                size_item.setText(get_file_display_size(size))
                size_item.setData(QVariant(size), USER_ROLE_SIZE)

            return size
        else:
            name_item = QStandardItem(name)
            name_item.setData(QVariant(file_icon), Qt.DecorationRole)
            name_item.setData(QVariant(ITEM_TYPE_FILE), USER_ROLE_ITEM_TYPE)

            size      = int(dw['s'])
            size_item = QStandardItem(get_file_display_size(size))
            size_item.setData(QVariant(size), USER_ROLE_SIZE)

            last_modified_item = create_last_modified_item(int(dw['l']))

            parent_item.appendRow([name_item, size_item, last_modified_item])

            return size

    expand(model.invisibleRootItem(), None, directory_walk)

    return model


class FilesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        if left.column() == 1: # size
            return left.data(USER_ROLE_SIZE).toInt()[0] < right.data(USER_ROLE_SIZE).toInt()[0]
        elif left.column() == 2: # last modified
            return left.data(USER_ROLE_LAST_MODIFIED).toInt()[0] < right.data(USER_ROLE_LAST_MODIFIED).toInt()[0]

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
        self.bin_directory           = posixpath.join(unicode(self.program.root_directory), 'bin')
        self.refresh_in_progress     = False
        self.available_files         = []
        self.available_directories   = []
        self.folder_icon             = QIcon(os.path.join(get_resources_path(), "folder-icon.png"))
        self.file_icon               = QIcon(os.path.join(get_resources_path(), "file-icon.png"))
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
        self.tree_files.activated.connect(self.rename_activated_file)
        self.button_upload_files.clicked.connect(show_upload_files_wizard)
        self.button_download_files.clicked.connect(self.download_selected_files)
        self.button_rename_file.clicked.connect(self.rename_selected_file)
        self.button_delete_files.clicked.connect(self.delete_selected_files)

        self.label_error.setVisible(False)

    def update_ui_state(self):
        selection_count = len(self.tree_files.selectionModel().selectedRows())

        self.set_widget_enabled(self.button_download_files, selection_count > 0)
        self.set_widget_enabled(self.button_rename_file, selection_count == 1)
        self.set_widget_enabled(self.button_delete_files, selection_count > 0)

    def close_all_dialogs(self):
        pass

    def refresh_files_done(self):
        self.refresh_in_progress = False
        self.update_main_ui_state()

    def refresh_files(self):
        def cb_directory_walk(result):
            if result == None or result.exit_code != 0:
                if result == None or len(result.stderr) == 0:
                    self.label_error.setText('<b>Error:</b> Internal error occurred')
                else:
                    self.label_error.setText('<b>Error:</b> ' + Qt.escape(result.stderr.decode('utf-8').strip()))

                self.label_error.setVisible(True)
                self.refresh_files_done()
                return

            self.label_error.setVisible(False)

            def expand_async(data):
                try:
                    directory_walk = json.loads(zlib.decompress(buffer(data)).decode('utf-8'))
                except:
                    directory_walk = None

                if directory_walk == None or not isinstance(directory_walk, dict):
                    available_files       = []
                    available_directories = []
                    directory_walk        = None
                else:
                    available_files, available_directories = expand_directory_walk_to_lists(directory_walk)

                return directory_walk, available_files, available_directories

            def cb_expand_success(result):
                directory_walk, available_files, available_directories = result

                self.available_files       = available_files
                self.available_directories = available_directories

                if directory_walk != None:
                    expand_directory_walk_to_model(directory_walk, self.tree_files_model, self.folder_icon, self.file_icon)
                else:
                    self.label_error.setText('<b>Error:</b> Received invalid data')
                    self.label_error.setVisible(True)

                self.tree_files.header().setSortIndicator(0, Qt.AscendingOrder)
                self.refresh_files_done()

            def cb_expand_error():
                # FIXME: report error
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

        self.script_manager.execute_script('directory_walk', cb_directory_walk,
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
            item_type = name_item.data(USER_ROLE_ITEM_TYPE).toInt()[0]

            if item_type == ITEM_TYPE_DIRECTORY:
                for i in range(name_item.rowCount()):
                    expand(name_item.child(i, 0))
            elif item_type == ITEM_TYPE_FILE:
                file_name = get_full_item_path(name_item)

                downloads.append(Download(file_name, unicode(QDir.toNativeSeparators(file_name))))

        for selected_name_item in selected_name_items:
            expand(selected_name_item)

        if len(downloads) == 0:
            return

        download_directory = unicode(QFileDialog.getExistingDirectory(get_main_window(), 'Download Files'))

        if len(download_directory) == 0:
            return

        # FIXME: on Mac OS X the getExistingDirectory() might return the directory with
        #        the last part being invalid, try to find the valid part of the directory
        if sys.platform == 'darwin':
            while len(download_directory) > 0 and not os.path.isdir(download_directory):
                download_directory = os.path.split(download_directory)[0]

        if len(download_directory) == 0:
            return

        self.show_download_wizard('files', download_directory, downloads)

    def rename_activated_file(self, index):
        if index.column() == 0:
            mapped_index = self.tree_files_proxy_model.mapToSource(index)
            name_item    = self.tree_files_model.itemFromIndex(mapped_index)
            item_type    = name_item.data(USER_ROLE_ITEM_TYPE).toInt()[0]

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
        item_type = name_item.data(USER_ROLE_ITEM_TYPE).toInt()[0]

        if item_type == ITEM_TYPE_FILE:
            title     = 'Rename File'
            type_name = 'file'
        else:
            title     = 'Rename Directory'
            type_name = 'directory'

        old_name = unicode(name_item.text())

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

        new_name = unicode(dialog.textValue())

        if new_name == old_name:
            return

        # check that new name is valid
        if len(new_name) == 0 or new_name == '.' or new_name == '..' or '/' in new_name:
            QMessageBox.critical(get_main_window(), title + ' Error',
                                 'A valid {0} name cannot be empty, cannot be one dot [.], cannot be two dots [..] and cannot contain a forward slash [/].'
                                 .format(type_name),
                                 QMessageBox.Ok)
            return

        # check that new name is not already in use
        name_item_parent = name_item.parent()

        if name_item_parent == None:
            name_item_parent = self.tree_files_model.invisibleRootItem()

        for i in range(name_item_parent.rowCount()):
            if new_name == unicode(name_item_parent.child(i).text()):
                QMessageBox.critical(get_main_window(), title + ' Error',
                                     'The new {0} name is already in use.'.format(type_name),
                                     QMessageBox.Ok)
                return

        absolute_old_name = posixpath.join(self.bin_directory, get_full_item_path(name_item))
        absolute_new_name = posixpath.join(posixpath.split(absolute_old_name)[0], new_name)

        def cb_rename(result):
            if result == None:
                QMessageBox.critical(get_main_window(), title + ' Error',
                                     u'Internal error during {0} rename'.format(type_name))
            elif result.exit_code != 0:
                QMessageBox.critical(get_main_window(), title + ' Error',
                                     u'Could not rename {0}:\n\n{1}'.format(type_name, result.stderr.strip()))
            else:
                name_item.setText(new_name)

                if self.tree_files.header().sortIndicatorSection() == 0:
                    self.tree_files.header().setSortIndicator(0, self.tree_files.header().sortIndicatorOrder())

        self.script_manager.execute_script('rename', cb_rename,
                                           [absolute_old_name, absolute_new_name])

    def delete_selected_files(self):
        button = QMessageBox.question(get_main_window(), 'Delete Files',
                                      'Irreversibly deleting selected files and directories.',
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if not self.is_alive() or button != QMessageBox.Ok:
            return

        selected_name_items = set(self.get_directly_selected_name_items())

        if len(selected_name_items) == 0:
            return

        def progress_canceled(sd_ref):
            sd = sd_ref[0]

            if sd == None:
                return

            self.script_manager.abort_script(sd)

        sd_ref   = [None]
        progress = ExpandingProgressDialog(self)
        progress.hide_progress_text()
        progress.setModal(True)
        progress.setWindowTitle('Delete Files')
        progress.setLabelText('Collecting files and directories to delete')
        progress.setRange(0, 0)
        progress.canceled.connect(lambda: progress_canceled(sd_ref))
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
            item_type = selected_name_item.data(USER_ROLE_ITEM_TYPE).toInt()[0]

            if item_type == ITEM_TYPE_DIRECTORY:
                dirs_to_delete.append(unicode(posixpath.join(self.bin_directory, path)))
            else:
                files_to_delete.append(unicode(posixpath.join(self.bin_directory, path)))

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

        def cb_program_delete_files_dirs(sd_ref, result):
            sd = sd_ref[0]

            if sd != None:
                aborted = sd.abort
            else:
                aborted = False

            sd_ref[0] = None

            progress.cancel()
            self.refresh_files()

            if aborted:
                QMessageBox.information(get_main_window(), 'Delete Files',
                                        u'Delete operation was aborted.')
            elif result == None:
                QMessageBox.critical(get_main_window(), 'Delete Files Error',
                                     u'Internal error during deletion.')
            elif result.exit_code != 0:
                QMessageBox.critical(get_main_window(), 'Delete Files Error',
                                     u'Could not delete selected files/directories:\n\n{0}'.format(result.stderr.strip()))

        sd_ref[0] = self.script_manager.execute_script('program_delete_files_dirs',
                                                       lambda result: cb_program_delete_files_dirs(sd_ref, result),
                                                       [json.dumps(files_to_delete), json.dumps(dirs_to_delete)],
                                                       execute_as_user=True)
