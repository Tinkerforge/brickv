# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
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

from PyQt4.QtCore import Qt, QVariant
from PyQt4.QtGui import QWidget, QStandardItemModel, QStandardItem, QFileDialog, QProgressDialog, QMessageBox, QSortFilterProxyModel
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.ui_program_info_logs import Ui_ProgramInfoLogs
from brickv.async_call import async_call
import os
import json

class LogsProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        # size
        if left.column() == 1:
            return left.data(Qt.UserRole + 1).toInt()[0] < right.data(Qt.UserRole + 1).toInt()[0]

        return QSortFilterProxyModel.lessThan(self, left, right)


class ProgramInfoLogs(QWidget, Ui_ProgramInfoLogs):
    def __init__(self, context, update_main_ui_state, set_widget_enabled, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)

        self.setupUi(self)

        self.session                = context.session
        self.script_manager         = context.script_manager
        self.program                = context.program
        self.update_main_ui_state   = update_main_ui_state
        self.set_widget_enabled     = set_widget_enabled
        self.root_directory         = unicode(self.program.root_directory)
        self.refresh_in_progress    = False
        self.tree_logs_model        = QStandardItemModel(self)
        self.tree_logs_model_header = ['Date / Time', 'Size']
        self.tree_logs_proxy_model  = LogsProxyModel(self)

        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_model_header)
        self.tree_logs_proxy_model.setSourceModel(self.tree_logs_model)
        self.tree_logs.setModel(self.tree_logs_proxy_model)
        self.tree_logs.setColumnWidth(0, 250)

        self.tree_logs.selectionModel().selectionChanged.connect(self.update_ui_state)
        self.button_download_logs.clicked.connect(self.download_selected_logs)
        self.button_delete_logs.clicked.connect(self.delete_selected_logs)

    def update_ui_state(self):
        has_selection = self.tree_logs.selectionModel().hasSelection()

        self.set_widget_enabled(self.button_download_logs, has_selection)
        self.set_widget_enabled(self.button_delete_logs, has_selection)

        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)

    def refresh_logs(self):
        def cb_program_get_os_walk(result):
            self.refresh_in_progress = False

            if result == None or result.stderr != "":
                self.update_main_ui_state()
                # TODO: Error popup for user?
                print result
                return

            def get_file_display_size(size):
                if size < 1024:
                    return str(size) + ' Bytes'
                else:
                    return str(size / 1024) + ' kiB'

            def create_file_size_item(size):
                item = QStandardItem(get_file_display_size(size))
                item.setData(QVariant(size))

                return item

            program_dir_walk_result = json.loads(result.stdout)

            for dir_node in program_dir_walk_result:
                if dir_node['root'] == os.path.join(self.root_directory, "log"):
                    for idx, f in enumerate(dir_node['files']):
                        file_name = f['name']
                        file_size = int(unicode(f['size']))
                        file_path = os.path.join(dir_node['root'], file_name)
                        if len(file_name.split('-')) < 2:
                            continue

                        if file_name.split('-')[0] == "continuous":
                            parent_continuous = None
                            for i in range(self.tree_logs_model.rowCount()):
                                if self.tree_logs_model.item(i).text() == "Continuous":
                                    parent_continuous = self.tree_logs_model.item(i)
                                    parent_continuous_size = self.tree_logs_model.item(i, 1)
                                    break

                            if parent_continuous:
                                if file_name.split('-')[1] == "stdout.log":
                                    parent_continuous.appendRow([QStandardItem("stdout.log"),
                                                                 create_file_size_item(file_size),
                                                                 QStandardItem("LOG_FILE_CONT"),
                                                                 QStandardItem(file_path)])
                                elif file_name.split('-')[1] == "stderr.log":
                                    parent_continuous.appendRow([QStandardItem("stderr.log"),
                                                                 create_file_size_item(file_size),
                                                                 QStandardItem("LOG_FILE_CONT"),
                                                                 QStandardItem(file_path)])
                                current_size = parent_continuous_size.data().toInt()[0]
                                new_file_size = current_size + file_size
                                parent_continuous_size.setText(get_file_display_size(new_file_size))
                                parent_continuous_size.setData(QVariant(new_file_size))
                            else:
                                parent_continuous = [QStandardItem("Continuous"),
                                                     create_file_size_item(file_size),
                                                     QStandardItem("PARENT_CONT"),
                                                     QStandardItem("")]
                                if file_name.split('-')[1] == "stdout.log":
                                    parent_continuous[0].appendRow([QStandardItem("stdout.log"),
                                                                    create_file_size_item(file_size),
                                                                    QStandardItem("LOG_FILE_CONT"),
                                                                    QStandardItem(file_path)])
                                elif file_name.split('-')[1] == "stderr.log":
                                    parent_continuous[0].appendRow([QStandardItem("stderr.log"),
                                                                    create_file_size_item(file_size),
                                                                    QStandardItem("LOG_FILE_CONT"),
                                                                    QStandardItem(file_path)])
                                self.tree_logs_model.appendRow(parent_continuous)

                            self.tree_logs.header().setSortIndicator(0, Qt.DescendingOrder)
                            self.update_ui_state()
                            continue

                        time_stamp = file_name.split('-')[0]
                        file_name_display = file_name.split('-')[1]

                        if len(time_stamp.split('T')) < 2:
                            continue
                        _date = time_stamp.split('T')[0]
                        _time = time_stamp.split('T')[1]
                        year = _date[:4]
                        month = _date[4:6]
                        day = _date[6:]
                        date = '-'.join([year, month, day])

                        if '+' in _time:
                            if len(_time.split('+')) < 2:
                                continue
                            __time = _time.split('+')[0].split('.')[0]
                            hour = __time[:2]
                            mins = __time[2:4]
                            sec = __time[4:]
                            gmt = _time.split('+')[1]
                            gmt = '+'+gmt
                        elif '-' in _time:
                            if len(_time.split('-')) < 2:
                                continue
                            __time = _time.split('-')[0].split('.')[0]
                            hour = __time[:2]
                            mins = __time[2:4]
                            sec = __time[4:]
                            gmt = _time.split('-')[1]
                            gmt = '-'+gmt
                        time = ':'.join([hour, mins, sec])
                        time_with_gmt = time+' '+gmt

                        parent_date = None
                        for i in range(self.tree_logs_model.rowCount()):
                            if self.tree_logs_model.item(i).text() == date:
                                parent_date = self.tree_logs_model.item(i)
                                parent_date_size = self.tree_logs_model.item(i, 1)
                                break

                        if parent_date:
                            found_parent_time = False
                            for i in range(parent_date.rowCount()):
                                if parent_date.child(i).text() == time:
                                    found_parent_time = True
                                    parent_date.child(i).appendRow([QStandardItem(file_name_display),
                                                                    create_file_size_item(file_size),
                                                                    QStandardItem("LOG_FILE"),
                                                                    QStandardItem(file_path)])
                                    current_size = parent_date.child(i, 1).data().toInt()[0]
                                    new_file_size = current_size + file_size
                                    parent_date.child(i, 1).setText(get_file_display_size(new_file_size))
                                    parent_date.child(i, 1).setData(QVariant(new_file_size))

                                    current_parent_size = parent_date_size.data().toInt()[0]
                                    new_parent_file_size = current_parent_size + file_size
                                    parent_date_size.setText(get_file_display_size(new_parent_file_size))
                                    parent_date_size.setData(QVariant(new_parent_file_size))
                                    break

                            if not found_parent_time:
                                parent_date.appendRow([QStandardItem(time),
                                                       create_file_size_item(file_size),
                                                       QStandardItem("PARENT_TIME"),
                                                       QStandardItem("")])
                                parent_date.child(parent_date.rowCount()-1).appendRow([QStandardItem(file_name_display),
                                                                                       create_file_size_item(file_size),
                                                                                       QStandardItem("LOG_FILE"),
                                                                                       QStandardItem(file_path)])
                                current_parent_size = parent_date_size.data().toInt()[0]
                                new_parent_file_size = current_parent_size + file_size
                                parent_date_size.setText(get_file_display_size(new_parent_file_size))
                                parent_date_size.setData(QVariant(new_parent_file_size))
                        else:
                            parent_date = [QStandardItem(date),
                                           create_file_size_item(file_size),
                                           QStandardItem("PARENT_DATE"),
                                           QStandardItem("")]
                            parent_date[0].appendRow([QStandardItem(time),
                                                      create_file_size_item(file_size),
                                                      QStandardItem("PARENT_TIME"),
                                                      QStandardItem("")])
                            parent_date[0].child(0).appendRow([QStandardItem(file_name_display),
                                                               create_file_size_item(file_size),
                                                               QStandardItem("LOG_FILE"),
                                                               QStandardItem(file_path)])
                            self.tree_logs_model.appendRow(parent_date)


            self.tree_logs.header().setSortIndicator(0, Qt.DescendingOrder)
            self.update_ui_state()

        self.refresh_in_progress = True
        self.update_main_ui_state()

        width = self.tree_logs.columnWidth(0)
        self.tree_logs_model.clear()
        self.tree_logs_model.setHorizontalHeaderLabels(self.tree_logs_model_header)
        self.tree_logs.setColumnWidth(0, width)

        self.script_manager.execute_script('program_get_os_walk',
                                           cb_program_get_os_walk,
                                           [self.root_directory])

    def load_log_files_for_ops(self, index_list):
        if len(index_list) % 4 != 0:
            return False

        index_list_chunked = zip(*[iter(index_list)] * 4)
        logs_download_dict = {'files': {}, 'total_download_size': 0}

        def populate_log_download(item_list):
            if item_list[2].text() == "PARENT_CONT":
                for i in range(item_list[0].rowCount()):
                    f_size = item_list[0].child(i, 1).data().toInt()[0] # File size
                    f_path = unicode(item_list[0].child(i, 3).text()) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] = \
                            logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "PARENT_DATE":
                for i in range(item_list[0].rowCount()):
                    parent_time = item_list[0].child(i)
                    for j in range(parent_time.rowCount()):
                        f_size = parent_time.child(j, 1).data().toInt()[0] # File size
                        f_path = unicode(parent_time.child(j, 3).text()) # File path
                        if not f_path in logs_download_dict['files']:
                            logs_download_dict['files'][f_path] = {'size': f_size}
                            logs_download_dict['total_download_size'] = \
                                logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "PARENT_TIME":
                for i in range(item_list[0].rowCount()):
                    f_size = item_list[0].child(i, 1).data().toInt()[0] # File size
                    f_path = unicode(item_list[0].child(i, 3).text()) # File path
                    if not f_path in logs_download_dict['files']:
                        logs_download_dict['files'][f_path] = {'size': f_size}
                        logs_download_dict['total_download_size'] = \
                            logs_download_dict['total_download_size'] + f_size

            elif item_list[2].text() == "LOG_FILE" or \
                 item_list[2].text() == "LOG_FILE_CONT":
                f_size = item_list[1].data().toInt()[0] # File size
                f_path = unicode(item_list[3].text()) # File path
                if not f_path in logs_download_dict['files']:
                    logs_download_dict['files'][f_path] = {'size': f_size}
                    logs_download_dict['total_download_size'] = \
                        logs_download_dict['total_download_size'] + f_size
            else:
                pass

        for index_chunk in index_list_chunked:
            item_list = []
            for index in index_chunk:
                item = self.tree_logs_model.itemFromIndex(self.tree_logs_proxy_model.mapToSource(index))
                item_list.append(item)
            populate_log_download(item_list)

        return logs_download_dict

    def download_selected_logs(self):
        def log_download_pd_closed():
            if len(log_files_to_download['files']) > 0:
                QMessageBox.warning(None,
                                    'Program | Logs',
                                    'Download could not finish.',
                                    QMessageBox.Ok)
            else:
                QMessageBox.information(None,
                                        'Program | Logs',
                                        'Download complete!',
                                        QMessageBox.Ok)

        self.tree_logs.setColumnHidden(2, False)
        self.tree_logs.setColumnHidden(3, False)
        index_list = self.tree_logs.selectedIndexes()
        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)
        if not index_list:
            return

        log_files_to_download = self.load_log_files_for_ops(index_list)
        if not log_files_to_download:
            return

        log_files_download_dir = unicode(QFileDialog.getExistingDirectory(self, "Choose Download Location"))

        if log_files_download_dir != "":
            log_download_pd = QProgressDialog(str(len(log_files_to_download['files']))+" file(s) remaining...",
                                              "Cancel",
                                              0,
                                              100,
                                              self)
            log_download_pd.setWindowTitle("Download Progress")
            log_download_pd.setAutoReset(False)
            log_download_pd.setAutoClose(False)
            log_download_pd.setMinimumDuration(0)
            log_download_pd.setValue(0)

            log_download_pd.canceled.connect(log_download_pd_closed)

            def cb_open(red_file):
                def cb_read_status(bytes_read, max_length):
                    files_remaining = str(len(log_files_to_download['files']))
                    current_percent = int(float(bytes_read)/float(max_length) * 100)

                    log_download_pd.setLabelText(files_remaining+" file(s) remaining...")
                    log_download_pd.setValue(current_percent)

                    if current_percent == 100:
                        log_download_pd.setValue(0)

                def cb_read(red_file, result):
                    red_file.release()
                    if result is not None:
                        # Success
                        read_file_path = log_files_to_download['files'].keys()[0]
                        save_file_name = ''.join(read_file_path.split('/')[-1:])
                        with open(os.path.join(unicode(log_files_download_dir),
                                               unicode(save_file_name)),
                                               'wb') as fh_log_write:
                            fh_log_write.write(result.data)

                        if read_file_path in log_files_to_download['files']:
                            log_files_to_download['files'].pop(read_file_path, None)

                        if len(log_files_to_download['files']) == 0:
                            log_download_pd.close()
                            return

                        if not log_download_pd.wasCanceled():
                            log_download_pd.setLabelText(str(len(log_files_to_download['files']))+" file(s) remaining...")
                            log_download_pd.setValue(0)
                            async_call(REDFile(self.session).open,
                                       (log_files_to_download['files'].keys()[0],
                                       REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                                       cb_open,
                                       cb_open_error)

                    else:
                        # TODO: Error popup for user?
                        log_download_pd.close()
                        print result

                red_file.read_async(log_files_to_download['files'].values()[0]['size'],
                                    lambda x: cb_read(red_file, x),
                                    cb_read_status)

            def cb_open_error(result):
                # TODO: Error popup for user?
                log_download_pd.close()
                print result

            if len(log_files_to_download['files']) > 0:
                async_call(REDFile(self.session).open,
                           (log_files_to_download['files'].keys()[0],
                           REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0),
                           cb_open,
                           cb_open_error)

    def delete_selected_logs(self):
        def cb_program_delete_logs(result):
            if result.stderr == "":
                if json.loads(result.stdout):
                    QMessageBox.information(None,
                                           'Program | Logs',
                                           'Deleted successfully!',
                                                  QMessageBox.Ok)
                else:
                    QMessageBox.critical(None,
                                         'Program | Logs',
                                         'Deletion failed',
                                               QMessageBox.Ok)
            else:
                pass
                # TODO: Error popup for user?

        self.tree_logs.setColumnHidden(2, False)
        self.tree_logs.setColumnHidden(3, False)
        index_list =  self.tree_logs.selectedIndexes()
        self.tree_logs.setColumnHidden(2, True)
        self.tree_logs.setColumnHidden(3, True)
        if not index_list:
            return

        log_files_to_delete = self.load_log_files_for_ops(index_list)

        if not log_files_to_delete:
            return

        file_list = []

        for f_path in log_files_to_delete['files']:
            file_list.append(f_path)

        if len(file_list) > 0:
            self.script_manager.execute_script('program_delete_logs',
                                               cb_program_delete_logs,
                                               [json.dumps(file_list)])
