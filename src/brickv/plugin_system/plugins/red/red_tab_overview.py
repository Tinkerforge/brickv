# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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

import json
import time
import sys
import zlib
from operator import itemgetter
import html

from PyQt5.QtCore import Qt, QSortFilterProxyModel, QTimer
from PyQt5.QtGui import QStandardItem, QStandardItemModel

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_overview import Ui_REDTabOverview
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red.script_manager import check_script_result
from brickv.config import get_use_fusion_gui_style

# constants
REFRESH_TIME = 3000 # in milliseconds
REFRESH_TIMEOUT = 500 # in milliseconds
DEFAULT_TVIEW_NIC_HEADER_WIDTH = 210 # in pixels
DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_FIRST = 210 # in pixels
DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER = 105 # in pixels

class ProcessesProxyModel(QSortFilterProxyModel):
    # overrides QSortFilterProxyModel.lessThan
    def lessThan(self, left, right):
        # cpu and mem
        if left.column() in [3, 4]:
            if right.data(Qt.UserRole + 1) is None:
                return QSortFilterProxyModel.lessThan(self, left, right)
            return left.data(Qt.UserRole + 1) < right.data(Qt.UserRole + 1)

        return QSortFilterProxyModel.lessThan(self, left, right)

class REDTabOverview(REDTab, Ui_REDTabOverview):
    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.is_tab_on_focus = False

        self.setup_tview_nic()
        self.setup_tview_process()

        self.refresh_timer = QTimer(self)
        self.refresh_counter = 0
        self.nic_time = 0

        self.label_error.hide()

        # For MAC progress bar text fix
        self.label_pbar_cpu.hide()
        self.label_pbar_memory.hide()
        self.label_pbar_storage.hide()

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh)
        self.button_refresh.clicked.connect(self.refresh_clicked)
        self.cbox_based_on.currentIndexChanged.connect(self.change_process_sort_order)
        self.tview_nic.header().sectionClicked.connect(self.cb_tview_nic_sort_indicator_changed)
        self.tview_process.header().sectionClicked.connect(self.cb_tview_process_sort_indicator_changed)

    def tab_on_focus(self):
        self.button_refresh.setText('Collecting data...')
        self.button_refresh.setDisabled(True)
        self.is_tab_on_focus = True
        self.script_manager.execute_script('overview', self.cb_overview,
                                           ["0.1"], max_length=1024*1024,
                                           decode_output_as_utf8=False)
        self.reset_tview_nic()

    def tab_off_focus(self):
        self.is_tab_on_focus = False
        self.refresh_timer.stop()

    def tab_destroy(self):
        pass

    def refresh_clicked(self):
        self.refresh_timer.stop()
        self.refresh_counter = REFRESH_TIME//REFRESH_TIMEOUT
        self.cb_refresh()

    def change_process_sort_order(self):
        if self.cbox_based_on.currentIndex() == 0:
            self.tview_process.header().setSortIndicator(3, Qt.DescendingOrder)
        elif self.cbox_based_on.currentIndex() == 1:
            self.tview_process.header().setSortIndicator(4, Qt.DescendingOrder)

    # the callbacks
    def cb_refresh(self):
        self.refresh_counter += 1
        if self.refresh_counter >= REFRESH_TIME//REFRESH_TIMEOUT:
            self.refresh_counter = 0
            self.refresh_timer.stop()
            self.button_refresh.setText('Collecting data...')
            self.button_refresh.setDisabled(True)
            self.script_manager.execute_script('overview', self.cb_overview,
                                               max_length=1024*1024, decode_output_as_utf8=False)
        else:
            self.button_refresh.setDisabled(False)
            self.button_refresh.setText('Refresh in ' + str((REFRESH_TIME//REFRESH_TIMEOUT - self.refresh_counter)/2.0) + "...")

    def cb_overview(self, result):
        # check if the tab is still on view or not
        if not self.is_tab_on_focus:
            self.refresh_timer.stop()
            return

        self.refresh_counter = 0
        self.refresh_timer.start(REFRESH_TIMEOUT)

        okay, message = check_script_result(result, decode_stderr=True)

        if not okay:
            self.label_error.setText('<b>Error:</b> ' + html.escape(message))
            self.label_error.show()
            return

        self.label_error.hide()

        try:
            data = json.loads(zlib.decompress(memoryview(result.stdout)).decode('utf-8'))

            days, days_remainder = divmod(int(data['uptime']), 24 * 60 * 60)
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

            cpu_percent = data['cpu_used']
            cpu_percent_v = int(data['cpu_used'])

            memory_used = self.bytes2human(int(data['mem_used']))
            memory_total = self.bytes2human(int(data['mem_total']))
            memory_percent = "%.1f" % ((float(memory_used) / float(memory_total)) * 100)
            memory_percent_v = int(memory_percent.split('.')[0])

            storage_used = self.bytes2human(int(data['disk_used']))
            storage_total = self.bytes2human(int(data['disk_total']))
            storage_percent = "%.1f" % ((float(storage_used) / float(storage_total)) * 100)
            storage_percent_v = int(storage_percent.split('.')[0])

            nic_data_dict = data['ifaces']
            processes_data_list = data['processes']
        except:
            # some parsing error due to malfromed or incomplete output occured.
            # ignore it and wait for the next update
            return

        self.label_uptime_value.setText(uptime)

        pbar_cpu_fmt = "{0}%".format(cpu_percent)
        pbar_memory_fmt = "{0}% [{1} of {2} MiB]".format(memory_percent, memory_used, memory_total)
        pbar_storage_fmt = "{0}% [{1} of {2} GiB]".format(storage_percent, storage_used, storage_total)

        if sys.platform == 'darwin' and not get_use_fusion_gui_style():
            self.label_pbar_cpu.show()
            self.label_pbar_memory.show()
            self.label_pbar_storage.show()
            self.label_pbar_cpu.setText(pbar_cpu_fmt)
            self.label_pbar_memory.setText(pbar_memory_fmt)
            self.label_pbar_storage.setText(pbar_storage_fmt)
        else:
            self.pbar_cpu.setFormat(pbar_cpu_fmt)
            self.pbar_memory.setFormat(pbar_memory_fmt)
            self.pbar_storage.setFormat(pbar_storage_fmt)

        self.pbar_cpu.setValue(cpu_percent_v)
        self.pbar_memory.setValue(memory_percent_v)
        self.pbar_storage.setValue(storage_percent_v)

        self.nic_item_model.removeRows(0, self.nic_item_model.rowCount())

        def _get_nic_transfer_rate(bytes_now, bytes_previous, delta_time):
            return "%.1f" % float(((bytes_now - bytes_previous) / delta_time) / 1024.0)

        new_time = time.time()
        delta = new_time - self.nic_time
        self.nic_time = new_time

        for i, key in enumerate(nic_data_dict):
            if key not in self.nic_previous_bytes:
                self.nic_time = time.time()
                self.nic_item_model.setItem(i, 0, QStandardItem(key))
                self.nic_item_model.setItem(i, 1, QStandardItem("Collecting data..."))
                self.nic_item_model.setItem(i, 2, QStandardItem("Collecting data..."))
            else:
                download_rate = _get_nic_transfer_rate(nic_data_dict[key][1],
                                                       self.nic_previous_bytes[key]['received'],
                                                       delta)

                upload_rate = _get_nic_transfer_rate(nic_data_dict[key][0],
                                                     self.nic_previous_bytes[key]['sent'],
                                                     delta)

                self.nic_item_model.setItem(i, 0, QStandardItem(key))
                self.nic_item_model.setItem(i, 1, QStandardItem(download_rate + " KiB/s"))
                self.nic_item_model.setItem(i, 2, QStandardItem(upload_rate + " KiB/s"))

            self.nic_previous_bytes[key] = {'sent': nic_data_dict[key][0],
                                            'received': nic_data_dict[key][1]}

        self.nic_item_model.sort(self.tview_nic_previous_sort['column_index'],
                                 self.tview_nic_previous_sort['order'])

        self.process_item_model.removeRows(0, self.process_item_model.rowCount())

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
            name = p['name']
            cmdline = p['cmd']

            if len(cmdline) == 0:
                cmdline = name

            item_name = QStandardItem(name)
            item_name.setToolTip(cmdline)
            self.process_item_model.setItem(i, 0, item_name)

            item_pid = QStandardItem(str(p['pid']))
            self.process_item_model.setItem(i, 1, item_pid)

            item_user = QStandardItem(p['user'])
            self.process_item_model.setItem(i, 2, item_user)

            cpu = p['cpu']
            item_cpu = QStandardItem(str(cpu / 10.0)+'%')
            item_cpu.setData(cpu)
            self.process_item_model.setItem(i, 3, item_cpu)

            mem = p['mem']
            item_mem = QStandardItem(str(mem / 10.0)+'%')
            item_mem.setData(mem)
            self.process_item_model.setItem(i, 4, item_mem)

        self.process_item_model.sort(self.tview_process_previous_sort['column_index'],
                                     self.tview_process_previous_sort['order'])

    def cb_tview_nic_sort_indicator_changed(self, column_index):
        self.tview_nic_previous_sort = {'column_index': column_index,\
                                        'order': self.tview_nic.header().sortIndicatorOrder()}

    def cb_tview_process_sort_indicator_changed(self, column_index):
        self.tview_process_previous_sort = {'column_index': column_index,\
                                            'order': self.tview_nic.header().sortIndicatorOrder()}

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
        self.nic_item_model = QStandardItemModel(0, 3, self)
        self.nic_item_model.setHorizontalHeaderItem(0, QStandardItem("Interface"))
        self.nic_item_model.setHorizontalHeaderItem(1, QStandardItem("Download"))
        self.nic_item_model.setHorizontalHeaderItem(2, QStandardItem("Upload"))
        self.nic_item_model.setItem(0, 0, QStandardItem("Collecting data..."))
        self.tview_nic.setModel(self.nic_item_model)
        self.tview_nic.setColumnWidth(0, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(1, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(2, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.header().setSortIndicator(1, Qt.DescendingOrder)
        self.tview_nic_previous_sort = {'column_index': 1, 'order': Qt.DescendingOrder}
        self.nic_item_model.sort(self.tview_nic_previous_sort['column_index'],
                                 self.tview_nic_previous_sort['order'])
        self.tview_nic_previous_sort = {'column_index': self.tview_nic_previous_sort['column_index'],\
                                        'order': self.tview_nic_previous_sort['order']}
        self.nic_previous_bytes = {}

    def setup_tview_process(self):
        self.process_item_model = QStandardItemModel(0, 5, self)
        self.process_item_model.setHorizontalHeaderItem(0, QStandardItem("Name"))
        self.process_item_model.setHorizontalHeaderItem(1, QStandardItem("PID"))
        self.process_item_model.setHorizontalHeaderItem(2, QStandardItem("User"))
        self.process_item_model.setHorizontalHeaderItem(3, QStandardItem("CPU"))
        self.process_item_model.setHorizontalHeaderItem(4, QStandardItem("Memory"))
        self.process_item_model.setItem(0, 0, QStandardItem("Collecting data..."))
        self.process_item_proxy_model = ProcessesProxyModel(self)
        self.process_item_proxy_model.setSourceModel(self.process_item_model)
        self.tview_process.setModel(self.process_item_proxy_model)
        self.tview_process.setColumnWidth(0, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_FIRST)
        self.tview_process.setColumnWidth(1, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(2, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(3, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.setColumnWidth(4, DEFAULT_TVIEW_PROCESS_HEADER_WIDTH_OTHER)
        self.tview_process.header().setSortIndicator(3, Qt.DescendingOrder)
        self.tview_process_previous_sort = {'column_index': 3, 'order': Qt.DescendingOrder}
        self.process_item_model.sort(self.tview_process_previous_sort['column_index'],
                                     self.tview_process_previous_sort['order'])
        self.tview_process_previous_sort = {'column_index': self.tview_process_previous_sort['column_index'],\
                                            'order': self.tview_process_previous_sort['order']}
        self.cbox_based_on.addItem("CPU")
        self.cbox_based_on.addItem("Memory")

    def reset_tview_nic(self):
        self.nic_item_model.clear()
        self.nic_previous_bytes.clear()
        self.nic_item_model.setHorizontalHeaderItem(0, QStandardItem("Interface"))
        self.nic_item_model.setHorizontalHeaderItem(1, QStandardItem("Download"))
        self.nic_item_model.setHorizontalHeaderItem(2, QStandardItem("Upload"))
        self.nic_item_model.setItem(0, 0, QStandardItem("Collecting data..."))
        self.tview_nic.setColumnWidth(0, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(1, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.setColumnWidth(2, DEFAULT_TVIEW_NIC_HEADER_WIDTH)
        self.tview_nic.header().setSortIndicator(self.tview_nic_previous_sort['column_index'],
                                                 self.tview_nic_previous_sort['order'])
