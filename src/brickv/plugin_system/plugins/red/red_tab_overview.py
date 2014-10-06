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

import os
from PyQt4 import Qt, QtCore, QtGui
from brickv.program_path import get_program_path
from brickv.plugin_system.plugins.red.ui_red_tab_overview import Ui_REDTabOverview
from brickv.plugin_system.plugins.red.api import *

# constants
REFRESH_TIMEOUT = 4000 # 4 seconds
BIN = '/usr/bin/python'
PARAM1 = '-c'
PARAM2 = '''
import psutil
"""
symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
def bytes2human(n):
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return '%.1f%s' % (value, s)
    return "%sB" % n
"""
cpu_pcnt = psutil.cpu_percent(2)

memory_pcnt = psutil.phymem_usage().percent
memory_used = psutil.used_phymem() / 1048576
memory_total = psutil.TOTAL_PHYMEM / 1048576

storage_pcnt = psutil.disk_usage("/").percent
storage_used = psutil.disk_usage("/").used / 1073741824
storage_total = psutil.disk_usage("/").total / 1073741824

"""
for s in symbols:
    memory_used = memory_used.strip(s)
    memory_total = memory_total.strip(s)
    storage_used = storage_used.strip(s)
    storage_total = storage_total.strip(s)"""

output = str(cpu_pcnt) + "," + str(memory_pcnt) + "," + \
str(memory_used) + "," + str(memory_total) + "," + str(storage_pcnt) + \
"," + str(storage_used) + "," + str(storage_total)
print output
'''

class REDTabOverview(QtGui.QWidget, Ui_REDTabOverview):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.red = 0

        self.refresh_timer = Qt.QTimer(self)
        self.pbutton_refresh.setIcon(QtGui.QIcon(os.path.join(get_program_path(), "red_tab_overview_refresh.png")))

        # connecting signals to slots
        self.pbutton_refresh.pressed.connect(self.cb_refresh)
        self.refresh_timer.timeout.connect(self.cb_refresh)

    def tab_on_focus(self):
        self.sin  = REDFile(self.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
        self.sout = REDPipe(self.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
        self.serr = self.sout
        self.rp = REDProcess(self.red)

        self.rp.state_changed_callback = self.cb_rp_state_changed
        self.rp.spawn(BIN, [PARAM1, PARAM2], [], '/', 0, 0, self.sin, self.sout, self.serr)

        self.refresh_timer.start(REFRESH_TIMEOUT)

    def tab_off_focus(self):
        self.refresh_timer.stop()

        if self.rp is not None:
            self.rp.state_changed_callback = None
            self.rp.release()
            self.rp = None

        if self.sin is not None:
            self.sin.release()
            self.sin = None

        if self.sout is not None:
            self.sout.release()
            self.sout = None

        if self.serr is not None:
            self.serr.release()
            self.serr = None

    # the callbacks
    def cb_refresh(self):
        self.refresh_timer.stop()

        self.rp = REDProcess(self.red)
        self.rp.state_changed_callback = self.cb_rp_state_changed

        self.rp.spawn(BIN, [PARAM1, PARAM2], [], '/', 0, 0, self.sin, self.sout, self.serr)

        self.refresh_timer.start(REFRESH_TIMEOUT)

    def cb_rp_state_changed(self, p):
        #print 'cb_spawn: ', p.state, p.timestamp, p.pid, p.exit_code
        csv_tokens = self.sout.read(256).strip().split(',')
        cpu_pcnt = csv_tokens[0].split('.')[0]
        memory_pcnt = csv_tokens[1].split('.')[0]
        memory_used = csv_tokens[2]
        memory_total = csv_tokens[3]
        storage_pcnt = csv_tokens[4].split('.')[0]
        storage_used = csv_tokens[5]
        storage_total = csv_tokens[6]

        print "cpu_pcnt = ", cpu_pcnt
        print "memory_pcnt = ", memory_pcnt
        print "memory_used = ", memory_used
        print "memory_total = ", memory_total
        print "storage_pcnt = ", storage_pcnt
        print "storage_used = ", storage_used
        print "storage_total = ", storage_total
        
        print "---------------------------------"
        
        if(cpu_pcnt != ""):
            self.pbar_cpu.setFormat(Qt.QString("%v%"))
            self.pbar_cpu.setValue(int(cpu_pcnt))
        
        if(memory_pcnt != "" and memory_used != "" and memory_total != ""):
            self.pbar_memory.setFormat(Qt.QString("%v% [%1 of %2 MB]").arg(memory_used, memory_total))
            self.pbar_memory.setValue(int(memory_pcnt))
        
        if(storage_pcnt != "" and storage_used != "" and storage_total != ""):
            self.pbar_storage.setFormat(Qt.QString("%v% [%1 of %2 GB]").arg(storage_used, storage_total))
            self.pbar_storage.setValue(int(storage_pcnt))
        
        self.rp.release()
