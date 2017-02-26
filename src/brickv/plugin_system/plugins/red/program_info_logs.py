# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014-2015, 2017 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

program_info_logs.py: Program Logs Info Widget

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

from PyQt4.QtCore import Qt, QDateTime
from PyQt4.QtGui import QIcon, QWidget, QStandardItemModel, QStandardItem, \
                        QMessageBox, QSortFilterProxyModel, QApplication

from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.program_utils import Download, get_file_display_size
from brickv.plugin_system.plugins.red.ui_program_info_logs import Ui_ProgramInfoLogs
from brickv.plugin_system.plugins.red.program_info_logs_view import ProgramInfoLogsView
from brickv.plugin_system.plugins.red.script_manager import check_script_result, report_script_result
from brickv.utils import get_main_window, get_home_path, get_existing_directory
from brickv.load_pixmap import load_pixmap

USER_ROLE_FILE_NAME = Qt.UserRole + 2
USER_ROLE_ITEM_TYPE = Qt.UserRole + 3
USER_ROLE_SIZE      = Qt.UserRole + 4

ITEM_TYPE_PARENT_CONT   = 1
ITEM_TYPE_PARENT_DATE   = 2
ITEM_TYPE_PARENT_TIME   = 3
ITEM_TYPE_LOG_FILE_CONT = 4
ITEM_TYPE_LOG_FILE      = 5


class LogsProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        if left.column() == 1: # size
            return left.data(USER_ROLE_SIZE) < right.data(USER_ROLE_SIZE)

        return QSortFilterProxyModel.lessThan(self, left, right)


class ProgramInfoLogs(QWidget, Ui_ProgramInfoLogs):
    def __init__(self, context, update_main_ui_state, set_widget_enabled, is_alive,
                 show_download_wizard, set_program_callbacks_enabled):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session                       = context.session
        self.script_manager                = context.script_manager
        self.program                       = context.program
        self.update_main_ui_state          = update_main_ui_state
        self.set_widget_enabled            = set_widget_enabled
        self.is_alive                      = is_alive
        self.show_download_wizard          = show_download_wizard
        self.set_program_callbacks_enabled = set_program_callbacks_enabled
        self.log_directory                 = posixpath.join(self.program.root_directory, 'log')
        self.refresh_in_progress           = False
        self.any_refresh_in_progress       = False # set from ProgramInfoMain.update_ui_state
        self.view_dialog                   = None
        self.file_icon                     = QIcon(load_pixmap('file-icon.png'))
        self.tree_logs_model               = QStandardItemModel(self)
        self.tree_logs_model_header        = ['Date/Time', 'Size']
        self.tree_logs_proxy_model         = LogsProxyModel(self)
        self.last_download_directory       = get_home_path()

        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_model_header)
        self.tree_logs_proxy_model.setSourceModel(self.tree_logs_model)
        self.tree_logs.setModel(self.tree_logs_proxy_model)
        self.tree_logs.setColumnWidth(0, 250)

        self.tree_logs.selectionModel().selectionChanged.connect(self.update_ui_state)
        self.tree_logs.activated.connect(self.view_activated_log)
        self.button_download_logs.clicked.connect(self.download_selected_logs)
        self.button_view_log.clicked.connect(self.view_selected_log)
        self.button_delete_logs.clicked.connect(self.delete_selected_logs)

        self.label_error.setVisible(False)

    def update_ui_state(self):
        selection_count = len(self.tree_logs.selectionModel().selectedRows())

        self.set_widget_enabled(self.button_download_logs, not self.any_refresh_in_progress and selection_count > 0)
        self.set_widget_enabled(self.button_view_log, not self.any_refresh_in_progress and selection_count == 1 and len(self.get_directly_selected_log_items()) == 1)
        self.set_widget_enabled(self.button_delete_logs, not self.any_refresh_in_progress and selection_count > 0)

    def close_all_dialogs(self):
        if self.view_dialog != None:
            self.view_dialog.close()

    def refresh_logs_done(self):
        self.refresh_in_progress = False
        self.update_main_ui_state()

    def refresh_logs(self):
        def cb_program_logs_list(result):
            okay, message = check_script_result(result, decode_stderr=True)

            if not okay:
                self.label_error.setText('<b>Error:</b> ' + Qt.escape(message))
                self.label_error.setVisible(True)
                self.refresh_logs_done()
                return

            try:
                # FIXME: do decompress in an async_call
                program_logs_list = json.loads(zlib.decompress(buffer(result.stdout)).decode('utf-8'))
            except:
                program_logs_list = None

            if program_logs_list == None or not isinstance(program_logs_list, dict):
                self.label_error.setText('<b>Error:</b> Received invalid data')
                self.label_error.setVisible(True)
                self.refresh_logs_done()
                return

            self.label_error.setVisible(False)

            def create_file_size_item(size):
                item = QStandardItem(get_file_display_size(size))
                item.setData(size, USER_ROLE_SIZE)

                return item

            def update_file_size_item(item, additional_size):
                current_size = item.data(USER_ROLE_SIZE)
                new_size     = current_size + additional_size

                item.setText(get_file_display_size(new_size))
                item.setData(new_size, USER_ROLE_SIZE)

            continuous_row = None
            date_rows      = {}
            time_rows      = {}

            for file_name, file_size in program_logs_list.iteritems():
                QApplication.processEvents()

                file_name_parts = file_name.split('_')

                if file_name_parts[0] == "continuous":
                    if len(file_name_parts) != 2:
                        continue

                    if continuous_row == None:
                        continuous_item = QStandardItem("Continuous")
                        continuous_item.setData(ITEM_TYPE_PARENT_CONT, USER_ROLE_ITEM_TYPE)

                        continuous_row = [continuous_item, create_file_size_item(0)]

                        self.tree_logs_model.appendRow(continuous_row)

                    log_item = QStandardItem(file_name_parts[1])
                    log_item.setData(self.file_icon, Qt.DecorationRole)
                    log_item.setData(file_name, USER_ROLE_FILE_NAME)
                    log_item.setData(ITEM_TYPE_LOG_FILE_CONT, USER_ROLE_ITEM_TYPE)

                    continuous_row[0].appendRow([log_item, create_file_size_item(file_size)])
                    update_file_size_item(continuous_row[1], file_size)
                else:
                    if len(file_name_parts) != 3:
                        continue

                    try:
                        timestamp = int(file_name_parts[1].split('+')[0]) / 1000000
                    except ValueError:
                        continue

                    date      = QDateTime.fromTime_t(timestamp).toString('yyyy-MM-dd')
                    time      = QDateTime.fromTime_t(timestamp).toString('HH:mm:ss')
                    date_time = date + 'T' + time

                    if date in date_rows:
                        date_row = date_rows[date]
                    else:
                        date_item = QStandardItem(date)
                        date_item.setData(ITEM_TYPE_PARENT_DATE, USER_ROLE_ITEM_TYPE)

                        date_row        = [date_item, create_file_size_item(0)]
                        date_rows[date] = date_row

                        self.tree_logs_model.appendRow(date_row)

                    if date_time in time_rows:
                        time_row = time_rows[date_time]
                    else:
                        time_item = QStandardItem(time)
                        time_item.setData(ITEM_TYPE_PARENT_TIME, USER_ROLE_ITEM_TYPE)

                        time_row             = [time_item, create_file_size_item(0)]
                        time_rows[date_time] = time_row

                        date_row[0].appendRow(time_row)

                    log_item = QStandardItem(file_name_parts[2])
                    log_item.setData(self.file_icon, Qt.DecorationRole)
                    log_item.setData(file_name, USER_ROLE_FILE_NAME)
                    log_item.setData(ITEM_TYPE_LOG_FILE, USER_ROLE_ITEM_TYPE)

                    time_row[0].appendRow([log_item, create_file_size_item(file_size)])
                    update_file_size_item(time_row[1], file_size)
                    update_file_size_item(date_row[1], file_size)

            self.tree_logs.header().setSortIndicator(0, Qt.DescendingOrder)
            self.refresh_logs_done()

        self.refresh_in_progress = True
        self.update_main_ui_state()

        width = self.tree_logs.columnWidth(0)
        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_model_header)
        self.tree_logs.setColumnWidth(0, width)

        self.script_manager.execute_script('program_logs_list', cb_program_logs_list,
                                           [self.log_directory], max_length=1024*1024,
                                           decode_output_as_utf8=False)

    def get_directly_selected_log_items(self):
        selected_indexes   = self.tree_logs.selectedIndexes()
        selected_log_items = []

        for selected_index in selected_indexes:
            if selected_index.column() == 0:
                mapped_index  = self.tree_logs_proxy_model.mapToSource(selected_index)
                selected_item = self.tree_logs_model.itemFromIndex(mapped_index)
                item_type     = selected_item.data(USER_ROLE_ITEM_TYPE)

                if item_type in [ITEM_TYPE_LOG_FILE, ITEM_TYPE_LOG_FILE_CONT]:
                    selected_log_items.append(selected_item)

        return selected_log_items

    def load_log_files_for_ops(self, index_list):
        logs_download_dict = {'files': {}, 'total_download_size': 0, 'foobar':[]}

        def populate_log_download(item_list):
            item_type = item_list[0].data(USER_ROLE_ITEM_TYPE)

            if item_type == ITEM_TYPE_PARENT_CONT:
                for i in range(item_list[0].rowCount()):
                    f_size = item_list[0].child(i, 1).data(USER_ROLE_SIZE) # File size
                    file_name = item_list[0].child(i, 0).data(USER_ROLE_FILE_NAME)
                    f_path = posixpath.join(self.log_directory, file_name) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] += f_size
                        logs_download_dict['foobar'].append(file_name)

            elif item_type == ITEM_TYPE_PARENT_DATE:
                for i in range(item_list[0].rowCount()):
                    parent_time = item_list[0].child(i)
                    for j in range(parent_time.rowCount()):
                        f_size = parent_time.child(j, 1).data(USER_ROLE_SIZE) # File size
                        file_name = parent_time.child(j, 0).data(USER_ROLE_FILE_NAME)
                        f_path = posixpath.join(self.log_directory, file_name) # File path
                        if not f_path in logs_download_dict['files']:
                            logs_download_dict['files'][f_path] = {'size': f_size}
                            logs_download_dict['total_download_size'] += f_size
                            logs_download_dict['foobar'].append(file_name)

            elif item_type == ITEM_TYPE_PARENT_TIME:
                for i in range(item_list[0].rowCount()):
                    f_size = item_list[0].child(i, 1).data(USER_ROLE_SIZE) # File size
                    file_name = item_list[0].child(i, 0).data(USER_ROLE_FILE_NAME)
                    f_path = posixpath.join(self.log_directory, file_name) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] += f_size
                        logs_download_dict['foobar'].append(file_name)

            elif item_type in [ITEM_TYPE_LOG_FILE, ITEM_TYPE_LOG_FILE_CONT]:
                f_size = item_list[1].data(USER_ROLE_SIZE) # File size
                file_name = item_list[0].data(USER_ROLE_FILE_NAME)
                f_path = posixpath.join(self.log_directory, file_name) # File path
                if not f_path in logs_download_dict['files']:
                    logs_download_dict['files'][f_path] = {'size': f_size}
                    logs_download_dict['total_download_size'] += f_size
                    logs_download_dict['foobar'].append(file_name)

        index_rows = []

        for index in index_list:
            if index.column() == 0:
                index_rows.append([index,
                                   index.sibling(index.row(), 1)])

        for index_row in index_rows:
            item_list = []
            for index in index_row:
                item = self.tree_logs_model.itemFromIndex(self.tree_logs_proxy_model.mapToSource(index))
                item_list.append(item)
            populate_log_download(item_list)

        return logs_download_dict

    def download_selected_logs(self):
        index_list = self.tree_logs.selectedIndexes()

        if len(index_list) == 0:
            return

        log_files_to_download = self.load_log_files_for_ops(index_list)

        if len(log_files_to_download['foobar']) == 0:
            return

        download_directory = get_existing_directory(get_main_window(), 'Download Logs',
                                                    self.last_download_directory)

        if len(download_directory) == 0:
            return

        self.last_download_directory = download_directory

        downloads = []

        for file_name in log_files_to_download['foobar']:
            downloads.append(Download(file_name, file_name))

        self.show_download_wizard('logs', download_directory, downloads)

    def view_activated_log(self, index):
        if index.column() == 0 and not self.any_refresh_in_progress:
            mapped_index = self.tree_logs_proxy_model.mapToSource(index)
            item         = self.tree_logs_model.itemFromIndex(mapped_index)
            item_type    = item.data(USER_ROLE_ITEM_TYPE)

            if item_type in [ITEM_TYPE_LOG_FILE, ITEM_TYPE_LOG_FILE_CONT]:
                self.view_log(item)

    def view_selected_log(self):
        selection_count = len(self.tree_logs.selectionModel().selectedRows())

        if selection_count != 1:
            return

        selected_log_items = self.get_directly_selected_log_items()

        if len(selected_log_items) != 1:
            return

        self.view_log(selected_log_items[0])

    def view_log(self, item):
        file_name = posixpath.join(self.log_directory, item.data(USER_ROLE_FILE_NAME))

        self.set_program_callbacks_enabled(False)

        self.view_dialog = ProgramInfoLogsView(self, self.session, file_name)
        self.view_dialog.exec_()
        self.view_dialog = None

        if self.is_alive():
            self.set_program_callbacks_enabled(True)

    # FIXME: make this work like delete_selected_files
    def delete_selected_logs(self):
        button = QMessageBox.question(get_main_window(), 'Delete Logs',
                                      'Irreversibly deleting selected logs.',
                                      QMessageBox.Ok, QMessageBox.Cancel)

        if not self.is_alive() or button != QMessageBox.Ok:
            return

        def cb_delete(result):
            self.refresh_logs()
            report_script_result(result, 'Delete Logs Error', 'Could not delete selected logs')

        index_list = self.tree_logs.selectedIndexes()

        if not index_list:
            return

        log_files_to_delete = self.load_log_files_for_ops(index_list)

        if not log_files_to_delete:
            return

        file_list = []

        for f_path in log_files_to_delete['files']:
            file_list.append(f_path)

        if len(file_list) > 0:
            self.script_manager.execute_script('delete', cb_delete,
                                               [json.dumps(file_list), json.dumps([])],
                                               execute_as_user=True)
