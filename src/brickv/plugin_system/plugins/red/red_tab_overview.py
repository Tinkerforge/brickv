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

from PyQt4 import Qt, QtCore, QtGui
from brickv.program_path import get_program_path
from brickv.plugin_system.plugins.red.ui_red_tab_overview import Ui_REDTabOverview
from brickv.plugin_system.plugins.red.api import *

from brickv.plugin_system.plugins.red.script_manager import ScriptManager

# constants
REFRESH_TIMEOUT = 4000 # 4 seconds

class REDTabOverview(QtGui.QWidget, Ui_REDTabOverview):
    qtcb_state_changed = pyqtSignal(ScriptManager.ScriptResult)
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.red = None
        
        self.qtcb_state_changed.connect(self.cb_state_changed)

        self.refresh_timer = Qt.QTimer(self)

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh)

    def tab_on_focus(self):
        ScriptManager.execute_script('overview', self.qtcb_state_changed.emit)

    def tab_off_focus(self):
        self.refresh_timer.stop()

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

    # the callbacks
    def cb_refresh(self):
        self.refresh_timer.stop()
        ScriptManager.execute_script('overview', self.qtcb_state_changed.emit)

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

        self.label_uptime_value.setText(str(uptime))

        self.pbar_cpu.setFormat(Qt.QString("%1%").arg(cpu_percent))
        self.pbar_cpu.setValue(cpu_percent_v)
    
        self.pbar_memory.setFormat(Qt.QString("%1% [%2 of %3 MiB]").arg(memory_percent, memory_used, memory_total))
        self.pbar_memory.setValue(memory_percent_v)
    
        self.pbar_storage.setFormat(Qt.QString("%1% [%2 of %3 GiB]").arg(storage_percent, storage_used, storage_total))
        self.pbar_storage.setValue(storage_percent_v)
