# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2021 Matthias Bolte <matthias@tinkerforge.com>

healthmonitor.py: GUI for health monitoring

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
import time
import csv
from datetime import datetime

from PyQt5.QtCore import Qt, QTimer, QModelIndex
from PyQt5.QtWidgets import QDialog, QHeaderView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem

from brickv.ui_healthmonitor import Ui_HealthMonitor
from brickv.async_call import async_call
from brickv.utils import get_modeless_dialog_flags, get_save_file_name, get_home_path
from brickv.devicesproxymodel import DevicesProxyModel
from brickv.infos import DeviceInfo, inventory, get_version_string

SETTLE_DURATION = 5.0 # seconds

class HealthMonitorWindow(QDialog, Ui_HealthMonitor):
    def __init__(self, parent):
        super().__init__(parent, get_modeless_dialog_flags())

        self.setupUi(self)

        self.ipcon_available = False

        self.button_save_report_to_csv_file.clicked.connect(self.save_report_to_csv_file)
        self.button_close.clicked.connect(self.hide)

        self.fixed_column_names = ['Name', 'UID', 'Position', 'FW Version', 'Metric Errors']
        self.dynamic_column_names = []
        self.metric_errors = {} # by uid
        self.old_values = {} # by uid, by metric name

        self.tree_view_model = QStandardItemModel(self)

        self.tree_view_proxy_model = DevicesProxyModel(self)
        self.tree_view_proxy_model.setSourceModel(self.tree_view_model)
        self.tree_view.setModel(self.tree_view_proxy_model)
        self.tree_view.setSortingEnabled(True)
        self.tree_view.header().setSortIndicator(2, Qt.AscendingOrder)
        self.tree_view.setExpandsOnDoubleClick(False)

        self.delayed_refresh_tree_view_timer = QTimer(self)
        self.delayed_refresh_tree_view_timer.timeout.connect(self.delayed_refresh_tree_view)
        self.delayed_refresh_tree_view_timer.setInterval(100)

        inventory.info_changed.connect(lambda: self.delayed_refresh_tree_view_timer.start())

        self.update_metric_values_timer = QTimer(self)
        self.update_metric_values_timer.timeout.connect(lambda: self.update_metric_values())
        self.update_metric_values_timer.setInterval(1000)
        self.update_metric_values_timer.start()

        self.refresh_tree_view()
        self.update_ui_state()

    def delayed_refresh_tree_view(self):
        self.delayed_refresh_tree_view_timer.stop()

        if self.isVisible():
            self.refresh_tree_view()

    def refresh_tree_view(self):
        sis = self.tree_view.header().sortIndicatorSection()
        sio = self.tree_view.header().sortIndicatorOrder()

        self.tree_view_model.clear()
        self.tree_view_model.setHorizontalHeaderLabels(self.fixed_column_names)

        self.dynamic_column_names = []
        column_offset = len(self.fixed_column_names)

        def create_and_append_row(info, parent):
            try:
                metric_names = info.plugin.get_health_metric_names()
            except:
                metric_names = []

            fw_version = QStandardItem(get_version_string(info.firmware_version_installed, replace_unknown='?'))

            if info.firmware_version_installed < info.firmware_version_latest:
                font = fw_version.font()
                font.setBold(True)
                fw_version.setFont(font)

            row = [QStandardItem(info.name),
                   QStandardItem(info.uid),
                   QStandardItem(info.position.title()),
                   fw_version,
                   QStandardItem(str(self.metric_errors.get(info.uid, 0)))]

            for metric_name in metric_names:
                try:
                    i = self.dynamic_column_names.index(metric_name)
                except:
                    self.dynamic_column_names.append(metric_name)

                    i = len(self.dynamic_column_names) - 1

                    self.tree_view_model.setHorizontalHeaderItem(column_offset + i, QStandardItem(metric_name))

                while len(row) <= column_offset + i:
                    row.append(QStandardItem())

                item = row[column_offset + i]

                old_timestamp, old_value = self.old_values.get(info.uid, {}).get(metric_name, (None, None))

                item.setText(str(old_value if old_value != None else '-'))

                if old_timestamp != None and old_timestamp + SETTLE_DURATION >= time.monotonic():
                    font = item.font()

                    if not font.bold():
                        font.setBold(True)
                        item.setFont(font)

            for item in row:
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)

            parent.appendRow(row)

            return row

        def recurse_on_device(info, parent):
            if not isinstance(info, DeviceInfo):
                return

            row = create_and_append_row(info, parent)

            for child in info.connections_values():
                recurse_on_device(child, row[0])

        for info in inventory.get_infos():
            if not isinstance(info, DeviceInfo):
                continue

            # if a device has a reverse connection, it will be handled as a child below
            if info.reverse_connection != None:
                continue

            row = create_and_append_row(info, self.tree_view_model)

            for child in info.connections_values():
                recurse_on_device(child, row[0])

        self.tree_view.setAnimated(False)
        self.tree_view.expandAll()
        self.tree_view.setAnimated(True)

        self.tree_view.setSortingEnabled(True)
        self.tree_view.header().setSortIndicator(sis, sio)
        self.tree_view.header().setStretchLastSection(False)
        self.tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        self.update_metric_values()

    def get_health_metric_values_async(self, uid, index, metric_values):
        if self.tree_view_model.itemFromIndex(index) == None:
            # FIXME: item was removed in the meantime?
            return

        column_offset = len(self.fixed_column_names)

        for metric_name, metric_value in metric_values.items():
            try:
                i = self.dynamic_column_names.index(metric_name)
            except:
                # FIXME: column for this metric was removed in the meantime?
                continue

            sibling = index.sibling(index.row(), column_offset + i)

            if not sibling.isValid():
                # FIXME: item for this metric was removed in the meantime?
                continue

            item = self.tree_view_model.itemFromIndex(sibling)

            if item == None:
                # FIXME: item for this metric was removed in the meantime?
                continue

            self.update_item_text(uid, item, metric_name, metric_value)

        metric_name = 'Metric Errors'
        sibling = index.sibling(index.row(), self.fixed_column_names.index(metric_name))
        item = self.tree_view_model.itemFromIndex(sibling)

        if item == None:
            # FIXME: item was removed in the meantime?
            return

        self.update_item_text(uid, item, metric_name, self.metric_errors.get(uid, 0))

    def update_item_text(self, uid, item, metric_name, new_value):
        new_timestamp = time.monotonic()
        old_timestamp, old_value = self.old_values.get(uid, {}).get(metric_name, (None, None))
        new_value_str = str(new_value)

        if item.text() != new_value_str:
            item.setText(new_value_str)

        if old_value != new_value:
            if uid not in self.old_values:
                self.old_values[uid] = {metric_name: (new_timestamp, new_value)}
            else:
                self.old_values[uid][metric_name] = (new_timestamp, new_value)

            font = item.font()

            if not font.bold():
                font.setBold(True)
                item.setFont(font)
        elif old_timestamp + SETTLE_DURATION < new_timestamp:
            font = item.font()

            if font.bold():
                font.setBold(False)
                item.setFont(font)

    def get_health_metric_values_error(self, uid, index):
        if uid in self.metric_errors:
            self.metric_errors[uid] += 1
        else:
            self.metric_errors[uid] = 1

        if self.tree_view_model.itemFromIndex(index) == None:
            # FIXME: item was removed in the meantime?
            return

        metric_name = 'Metric Errors'
        sibling = index.sibling(index.row(), self.fixed_column_names.index(metric_name))
        item = self.tree_view_model.itemFromIndex(sibling)

        if item == None:
            # FIXME: item was removed in the meantime?
            return

        self.update_item_text(uid, item, metric_name, self.metric_errors[uid])

    def update_metric_values(self, parent=None):
        if not self.isVisible():
            return

        self.update_metric_values_timer.stop()

        if parent == None:
            parent = self.tree_view_model.invisibleRootItem()

        def make_async_call(info, uid, index):
            async_call(info.plugin.get_health_metric_values, None,
                       lambda metric_values: self.get_health_metric_values_async(uid, index, metric_values),
                       lambda: self.get_health_metric_values_error(uid, index))

        # FIXME: avoid getter burst!
        for r in range(parent.rowCount()):
            child = parent.child(r, 0)
            index = child.index()
            uid = parent.child(r, 1).text()
            info = inventory.get_info(uid)

            if info == None:
                # FIXME: unknown UID, remove row or mark it as broken?
                continue

            make_async_call(info, uid, index)

            self.update_metric_values(parent=child)

        async_call(lambda: None, None, self.update_metric_values_timer.start, None)

    def collect_metric_values(self, parent=None, indent=''):
        if parent == None:
            parent = self.tree_view_model.invisibleRootItem()

        rows = []

        for r in range(parent.rowCount()):
            row = []

            for c in range(parent.columnCount()):
                child = parent.child(r, c)

                if child == None:
                    text = ''
                else:
                    text = child.text()
                    font = child.font()

                    if c == 0:
                        text = indent + text

                    if font.bold():
                        text += ' <!>'

                row.append(text)

            rows.append(row)
            rows += self.collect_metric_values(parent=parent.child(r, 0), indent=indent + '  ')

        return rows

    def save_report_to_csv_file(self):
        date = datetime.now().replace(microsecond=0).isoformat().replace('T', '_').replace(':', '-')
        filename = get_save_file_name(self, 'Save Report To CSV File', os.path.join(get_home_path(), 'brickv_health_report_{0}.csv'.format(date)))

        if len(filename) == 0:
            return

        c = 0
        header = []

        while True:
            item = self.tree_view_model.horizontalHeaderItem(c)

            if item == None:
                break

            header.append(item.text())

            c += 1

        rows = [header] + self.collect_metric_values()

        try:
            with open(filename, 'w', newline='') as f:
                csv.writer(f).writerows(rows)
        except Exception as e:
            QMessageBox.critical(self, 'Save Report To CSV File',
                                 'Could not save report to CSV file:\n\n' + str(e),
                                 QMessageBox.Ok)

    def update_ui_state(self):
        pass

    def set_ipcon_available(self, ipcon_available):
        self.ipcon_available = ipcon_available

        self.update_ui_state()
