# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_overview.py: RED overview tab implementation

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

from PyQt4 import QtCore, Qt, QtGui
from brickv.plugin_system.plugins.red.ui_red_tab_overview import Ui_REDTabOverview
from brickv.plugin_system.plugins.red.api import *
import json
from operator import itemgetter
import time

# constants
REFRESH_TIME = 3000 # in milliseconds
REFRESH_TIMEOUT = 500 # in milliseconds
DEFAULT_TVIEW_NIC_HEADER_WIDTH = 210 # in pixels
DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_FIRST = 210 # in pixels
DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER = 105 # in pixels

class ProcessesProxyModel(QtGui.QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        # cpu and mem
        if left.column() in [3, 4]:
            return left.data(QtCore.Qt.UserRole + 1).toInt()[0] < right.data(QtCore.Qt.UserRole + 1).toInt()[0]

        return QtGui.QSortFilterProxyModel.lessThan(self, left, right)

class REDTabOverview(QtGui.QWidget, Ui_REDTabOverview):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.is_tab_on_focus = False

        self.setup_tview_nic()
        self.setup_tview_process()

        self.refresh_timer = Qt.QTimer(self)
        self.refresh_counter = 0
        self.nic_time = 0

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh)
        self.button_refresh.clicked.connect(self.refresh_clicked)
        self.cbox_based_on.currentIndexChanged.connect(self.change_process_sort_order)
        self.tview_nic_horizontal_header.sortIndicatorChanged.connect(self.cb_tview_nic_sort_indicator_changed)
        self.tview_process_horizontal_header.sortIndicatorChanged.connect(self.cb_tview_process_sort_indicator_changed)

    def tab_on_focus(self):
        self.button_refresh.setText('Gathering data...')
        self.button_refresh.setDisabled(True)
        self.is_tab_on_focus = True
        self.script_manager.execute_script('overview',
                                           self.cb_state_changed,
                                           ["0.1"])
        self.reset_tview_nic()

    def tab_off_focus(self):
        self.is_tab_on_focus = False
        self.refresh_timer.stop()

    def refresh_clicked(self):
        self.refresh_timer.stop()
        self.refresh_counter = REFRESH_TIME/REFRESH_TIMEOUT
        self.cb_refresh()

    def change_process_sort_order(self):
        if self.cbox_based_on.currentIndex() == 0:
            self.tview_process.horizontalHeader().setSortIndicator(3, QtCore.Qt.DescendingOrder)
        elif self.cbox_based_on.currentIndex() == 1:
            self.tview_process.horizontalHeader().setSortIndicator(4, QtCore.Qt.DescendingOrder)

    # the callbacks
    def cb_refresh(self):
        self.refresh_counter += 1
        if self.refresh_counter >= REFRESH_TIME/REFRESH_TIMEOUT:
            self.refresh_counter = 0
            self.refresh_timer.stop()
            self.button_refresh.setText('Gathering data...')
            self.button_refresh.setDisabled(True)
            self.script_manager.execute_script('overview',
                                               self.cb_state_changed)
        else:
            self.button_refresh.setDisabled(False)
            self.button_refresh.setText('Refresh in ' + str((REFRESH_TIME/REFRESH_TIMEOUT - self.refresh_counter)/2.0) + "...")

    def cb_state_changed(self, result):
        #check if the tab is still on view or not
        if not self.is_tab_on_focus:
            self.refresh_timer.stop()
            return

        self.refresh_counter = 0
        self.refresh_timer.start(REFRESH_TIMEOUT)
        if result == None:
            return

        csv_tokens = result.stdout.split('\n')
        for i, t in enumerate(csv_tokens):
            if t == "" and i < len(csv_tokens) - 1:
                return

        _uptime = csv_tokens[0]
        days, days_remainder = divmod(int(_uptime), 24 * 60 * 60)
        hours, hours_remainder = divmod(days_remainder, 60 * 60)
        minutes, _ = divmod(hours_remainder, 60)
        uptime = ''

        if days > 0:
            uptime += str(days)

            if days == 1:
                uptime += ' day '
            else:
                uptime += ' days '

        if hours > 0:
            uptime += str(hours)

            if hours == 1:
                uptime += ' hour '
            else:
                uptime += ' hours '

        uptime += str(minutes)

        if minutes == 1:
            uptime += ' minute'
        else:
            uptime += ' minutes'

        cpu_percent = csv_tokens[1]
        cpu_percent_v = int(csv_tokens[1].split('.')[0])

        memory_used = self.bytes2human(int(csv_tokens[2]))
        memory_total = self.bytes2human(int(csv_tokens[3]))
        memory_percent = str("%.1f" % ((float(memory_used) / float(memory_total)) * 100))
        memory_percent_v = int(memory_percent.split('.')[0])

        storage_used = self.bytes2human(int(csv_tokens[4]))
        storage_total = self.bytes2human(int(csv_tokens[5]))
        storage_percent = str("%.1f" % ((float(storage_used) / float(storage_total)) * 100))
        storage_percent_v = int(storage_percent.split('.')[0])

        nic_data_dict = json.loads(csv_tokens[6])
        processes_data_list = json.loads(csv_tokens[7])

        self.label_uptime_value.setText(str(uptime))

        self.pbar_cpu.setFormat("{0}%".format(cpu_percent))
        self.pbar_cpu.setValue(cpu_percent_v)

        self.pbar_memory.setFormat("{0}% [{1} of {2} MiB]".format(memory_percent, memory_used, memory_total))
        self.pbar_memory.setValue(memory_percent_v)

        self.pbar_storage.setFormat("{0}% [{1} of {2} GiB]".format(storage_percent, storage_used, storage_total))
        self.pbar_storage.setValue(storage_percent_v)

        self.nic_item_model.removeRows(0, self.nic_item_model.rowCount())
        self.tview_nic.clearSpans()

        def _get_nic_transfer_rate(bytes_now, bytes_previous, delta_time):
            return "%.1f" % float(((bytes_now - bytes_previous) / delta_time) / 1000)

        new_time = time.time()
        delta = new_time - self.nic_time
        self.nic_time = new_time

        for i, key in enumerate(nic_data_dict):
            if key not in self.nic_previous_bytes:
                self.nic_time = time.time()
                self.nic_item_model.setItem(i, 0, Qt.QStandardItem(key))
                self.nic_item_model.setItem(i, 1, Qt.QStandardItem("Collecting data..."))
                self.nic_item_model.setItem(i, 2, Qt.QStandardItem("Collecting data..."))
            else:

                download_rate = _get_nic_transfer_rate(nic_data_dict[key][1],
                                                       self.nic_previous_bytes[key]['received'],
                                                       delta)

                upload_rate = _get_nic_transfer_rate(nic_data_dict[key][0],
                                                     self.nic_previous_bytes[key]['sent'],
                                                     delta)

                self.nic_item_model.setItem(i, 0, Qt.QStandardItem(key))
                self.nic_item_model.setItem(i, 1, Qt.QStandardItem(download_rate + " KB/s"))
                self.nic_item_model.setItem(i, 2, Qt.QStandardItem(upload_rate + " KB/s"))

            self.nic_previous_bytes[str(key)] = {'sent': nic_data_dict[key][0],
                                                 'received': nic_data_dict[key][1]}

        self.tview_nic.horizontalHeader().setSortIndicator(self.tview_nic_previous_sort['column_index'],
                                                           self.tview_nic_previous_sort['order'])

        self.process_item_model.removeRows(0, self.process_item_model.rowCount())
        self.tview_process.clearSpans()

        if self.cbox_based_on.currentIndex() == 0:
            processes_data_list_sorted = sorted(processes_data_list,
                                                key=itemgetter('cpu'),
                                                reverse=True)
        elif self.cbox_based_on.currentIndex() == 1:
            processes_data_list_sorted = sorted(processes_data_list,
                                                key=itemgetter('mem'),
                                                reverse=True)

        processes_data_list_sorted = processes_data_list_sorted[:self.sbox_number_of_process.value()]

        for i, p in enumerate(processes_data_list_sorted):
            _item_cmd = Qt.QStandardItem(unicode(processes_data_list_sorted[i]['cmd']))
            self.process_item_model.setItem(i, 0, _item_cmd)

            _item_pid = Qt.QStandardItem(unicode(processes_data_list_sorted[i]['pid']))
            self.process_item_model.setItem(i, 1, _item_pid)

            _item_usr = Qt.QStandardItem(unicode(processes_data_list_sorted[i]['usr']))
            self.process_item_model.setItem(i, 2, _item_usr)

            cpu = processes_data_list_sorted[i]['cpu']
            _item_cpu = Qt.QStandardItem(unicode(cpu / 10.0)+'%')
            _item_cpu.setData(QtCore.QVariant(cpu))
            self.process_item_model.setItem(i, 3, _item_cpu)

            mem = processes_data_list_sorted[i]['mem']
            _item_mem = Qt.QStandardItem(unicode(mem / 10.0)+'%')
            _item_mem.setData(QtCore.QVariant(mem))
            self.process_item_model.setItem(i, 4, _item_mem)

        self.tview_process.horizontalHeader().setSortIndicator(self.tview_process_previous_sort['column_index'],
                                                               self.tview_process_previous_sort['order'])

    def cb_tview_nic_sort_indicator_changed(self, column_index, order):
        self.tview_nic_previous_sort = {'column_index': column_index, 'order': order}

    def cb_tview_process_sort_indicator_changed(self, column_index, order):
        self.tview_process_previous_sort = {'column_index': column_index, 'order': order}

    #tab specific functions
    def bytes2human(self, n):
        symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
        prefix = {}
        for i, s in enumerate(symbols):
            prefix[s] = 1 << (i + 1) * 10
        for s in reversed(symbols):
            if n >= prefix[s]:
                value = float(n) / prefix[s]
                return "%.2f" % value
        return "%.2f" % n

    def setup_tview_nic(self):
        self.nic_item_model = Qt.QStandardItemModel(0, 3, self)
        self.nic_item_model.setHorizontalHeaderItem(0, Qt.QStandardItem("Interface"))
        self.nic_item_model.setHorizontalHeaderItem(1, Qt.QStandardItem("Download"))
        self.nic_item_model.setHorizontalHeaderItem(2, Qt.QStandardItem("Upload"))
        self.tview_nic.setSpan(0, 0, 1, 3)
        self.nic_item_model.setItem(0, 0, Qt.QStandardItem("Collecting data..."))
        self.tview_nic.setModel(self.nic_item_model)
        self.tview_nic.setColumnWidth(0, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(1, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(2, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.horizontalHeader().setSortIndicator(1, QtCore.Qt.DescendingOrder)
        self.tview_nic_previous_sort = {'column_index': 1, 'order': QtCore.Qt.DescendingOrder}
        self.tview_nic_horizontal_header = self.tview_nic.horizontalHeader()
        self.nic_previous_bytes = {}

    def setup_tview_process(self):
        self.process_item_model = Qt.QStandardItemModel(0, 5, self)
        self.process_item_model.setHorizontalHeaderItem(0, Qt.QStandardItem("Command"))
        self.process_item_model.setHorizontalHeaderItem(1, Qt.QStandardItem("PID"))
        self.process_item_model.setHorizontalHeaderItem(2, Qt.QStandardItem("User"))
        self.process_item_model.setHorizontalHeaderItem(3, Qt.QStandardItem("CPU"))
        self.process_item_model.setHorizontalHeaderItem(4, Qt.QStandardItem("Memory"))
        self.tview_process.setSpan(0, 0, 1, 5)
        self.process_item_model.setItem(0, 0, Qt.QStandardItem("Collecting data..."))
        self.process_item_proxy_model = ProcessesProxyModel(self)
        self.process_item_proxy_model.setSourceModel(self.process_item_model)
        self.tview_process.setModel(self.process_item_proxy_model)
        self.tview_process.setColumnWidth(0, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_FIRST)
        self.tview_process.setColumnWidth(1, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(2, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(3, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(4, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.horizontalHeader().setSortIndicator(3, QtCore.Qt.DescendingOrder)
        self.tview_process_previous_sort = {'column_index': 3, 'order': QtCore.Qt.DescendingOrder}
        self.tview_process_horizontal_header = self.tview_process.horizontalHeader()
        self.cbox_based_on.addItem("CPU")
        self.cbox_based_on.addItem("Memory")

    def reset_tview_nic(self):
        self.nic_item_model.clear()
        self.nic_previous_bytes.clear()
        self.nic_item_model.setHorizontalHeaderItem(0, Qt.QStandardItem("Interface"))
        self.nic_item_model.setHorizontalHeaderItem(1, Qt.QStandardItem("Download"))
        self.nic_item_model.setHorizontalHeaderItem(2, Qt.QStandardItem("Upload"))
        self.nic_item_model.setItem(0, 0, Qt.QStandardItem("Collecting data..."))
        self.tview_nic.setColumnWidth(0, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(1, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(2, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setSpan(0, 0, 1, 3)
        self.tview_nic.horizontalHeader().setSortIndicator(self.tview_nic_previous_sort['column_index'],
                                                           self.tview_nic_previous_sort['order'])
