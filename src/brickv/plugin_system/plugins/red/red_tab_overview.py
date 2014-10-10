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

import json
from PyQt4 import Qt, QtCore, QtGui
from brickv.program_path import get_program_path
from brickv.plugin_system.plugins.red.ui_red_tab_overview import Ui_REDTabOverview
from brickv.plugin_system.plugins.red.api import *

from brickv.plugin_system.plugins.red.script_manager import ScriptManager

# constants
REFRESH_TIMEOUT = 2000 # 2 seconds

class REDTabOverview(QtGui.QWidget, Ui_REDTabOverview):
    qtcb_state_changed = pyqtSignal(ScriptManager.ScriptResult)
    red = None
    script_manager = None
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.nic_item_model = Qt.QStandardItemModel(0, 3, self)
        self.nic_item_model.setHorizontalHeaderItem(0, Qt.QStandardItem(Qt.QString("Interface")))
        self.nic_item_model.setHorizontalHeaderItem(1, Qt.QStandardItem(Qt.QString("Download")))
        self.nic_item_model.setHorizontalHeaderItem(2, Qt.QStandardItem(Qt.QString("Upload")))
        default_item = Qt.QStandardItem(Qt.QString("Please wait..."))
        self.tview_nic.setSpan(0, 0, 1, 3)
        self.tview_nic.verticalHeader().hide()
        self.nic_item_model.setItem(0, 0, default_item)
        self.tview_nic.setModel(self.nic_item_model)
        self.tview_nic.horizontalHeader().setResizeMode(QtGui.QHeaderView.ResizeToContents)

        self.nic_previous_bytes = {}

        self.refresh_timer = Qt.QTimer(self)

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh)
        self.qtcb_state_changed.connect(self.cb_state_changed)

    def tab_on_focus(self):
        self.script_manager.execute_script('overview', self.qtcb_state_changed.emit, ["0.1"])

    def tab_off_focus(self):
        self.refresh_timer.stop()
        self.reset_tview_nic()

    # the callbacks
    def cb_refresh(self):
        self.refresh_timer.stop()
        self.script_manager.execute_script('overview', self.qtcb_state_changed.emit)

    def cb_state_changed(self, result):
        self.refresh_timer.start(REFRESH_TIMEOUT)
        if result == None:
            return
        
        csv_tokens = result.stdout.split('\n')
        for i, t in enumerate(csv_tokens):
            if t == "" and i < len(csv_tokens) - 1:
                return

        _uptime = csv_tokens[0]
        hrs, hrs_remainder = divmod(int(_uptime), 60 * 60)
        mins, _ = divmod(hrs_remainder, 60)
        uptime = str(hrs) + " hour " + str(mins) + " minutes"

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

        self.label_uptime_value.setText(str(uptime))

        self.pbar_cpu.setFormat(Qt.QString("%1%").arg(cpu_percent))
        self.pbar_cpu.setValue(cpu_percent_v)
    
        self.pbar_memory.setFormat(Qt.QString("%1% [%2 of %3 MiB]").arg(memory_percent, memory_used, memory_total))
        self.pbar_memory.setValue(memory_percent_v)
    
        self.pbar_storage.setFormat(Qt.QString("%1% [%2 of %3 GiB]").arg(storage_percent, storage_used, storage_total))
        self.pbar_storage.setValue(storage_percent_v)

        self.nic_item_model.removeRows(0, self.nic_item_model.rowCount())

        for i, key in enumerate(nic_data_dict):
            if key not in self.nic_previous_bytes:
                self.nic_item_model.setItem(i, 0, Qt.QStandardItem(Qt.QString(key)))
                self.nic_item_model.setItem(i, 1, Qt.QStandardItem(Qt.QString("Please wait...")))
                self.nic_item_model.setItem(i, 2, Qt.QStandardItem(Qt.QString("Please wait...")))
            else:
                #download
                download_rate = str(float(((nic_data_dict[key][1] - \
                self.nic_previous_bytes[key]['received']) / (REFRESH_TIMEOUT/1000))/1000))

                #upload
                upload_rate = str(float(((nic_data_dict[key][0] - \
                self.nic_previous_bytes[key]['sent']) / (REFRESH_TIMEOUT/1000)) /1000))

                self.nic_item_model.setItem(i, 0, Qt.QStandardItem(Qt.QString(key)))
                self.nic_item_model.setItem(i, 1, Qt.QStandardItem(Qt.QString(download_rate + " KB/s")))
                self.nic_item_model.setItem(i, 2, Qt.QStandardItem(Qt.QString(upload_rate + " KB/s")))

            self.nic_previous_bytes[str(key)] = {'sent': nic_data_dict[key][0], 'received': nic_data_dict[key][1]}

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

    def reset_tview_nic(self):
        self.nic_item_model.clear()
        self.nic_previous_bytes.clear()
        self.nic_item_model.setHorizontalHeaderItem(0, Qt.QStandardItem(Qt.QString("Interface")))
        self.nic_item_model.setHorizontalHeaderItem(1, Qt.QStandardItem(Qt.QString("Download")))
        self.nic_item_model.setHorizontalHeaderItem(2, Qt.QStandardItem(Qt.QString("Upload")))
        self.nic_item_model.setItem(0, 0, Qt.QStandardItem(Qt.QString("Please wait...")))
        self.tview_nic.setSpan(0, 0, 1, 3)
