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

# constants
REFRESH_TIMEOUT = 2000 # 2 seconds
BIN = '/usr/bin/python'
PARAM1 = '-c'
PARAM2 = '''
import psutil

def bytes2human(n):
    symbols = ('K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y')
    prefix = {}
    for i, s in enumerate(symbols):
        prefix[s] = 1 << (i + 1) * 10
    for s in reversed(symbols):
        if n >= prefix[s]:
            value = float(n) / prefix[s]
            return "%.2f" % value
    return "%.2f" % n

with open("/proc/uptime", "r") as utf:
    _uptime = utf.readline().split()[0].split(".")[0]
    hrs, hrs_remainder = divmod(int(_uptime), 60 * 60)
    min, ignore = divmod(hrs_remainder, 60)
    uptime = str(hrs) + " hour " + str(min) + " minutes"
    utf.close()

cpu_pcnt = psutil.cpu_percent(1)
memory_pcnt = (float(psutil.phymem_usage().used) / float(psutil.phymem_usage().total)) * 100
memory_used = bytes2human(psutil.used_phymem())
memory_total = bytes2human(psutil.TOTAL_PHYMEM)
storage_pcnt = psutil.disk_usage("/").percent
storage_used = bytes2human(psutil.disk_usage("/").used)
storage_total = bytes2human(psutil.disk_usage("/").total)

output = str(uptime) + "," + str(cpu_pcnt) + "," + str(memory_pcnt) + "," + \
str(memory_used) + "," + str(memory_total) + "," + str(storage_pcnt) + \
"," + str(storage_used) + "," + str(storage_total)
print output
'''

class REDTabOverview(QtGui.QWidget, Ui_REDTabOverview):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.red = None
        self.sin = None
        self.sout = None
        self.serr = None
        self.rp = None

        self.refresh_timer = Qt.QTimer(self)

        # connecting signals to slots
        self.refresh_timer.timeout.connect(self.cb_refresh)

    def tab_on_focus(self):
        self.sin = REDFile(self.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
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
        #print "GOT = ", self.sout.read(256).strip().split(',')
        
        if p.state == REDProcess.STATE_EXITED:
            csv_tokens = self.sout.read(256).strip().split(',')
            uptime = csv_tokens[0]
            cpu_pcnt = csv_tokens[1].split('.')[0]
            memory_pcnt = csv_tokens[2].split('.')[0]
            memory_used = csv_tokens[3]
            memory_total = csv_tokens[4]
            storage_pcnt = csv_tokens[5].split('.')[0]
            storage_used = csv_tokens[6]
            storage_total = csv_tokens[7]

            print "uptime  = ", uptime
            print "cpu_pcnt = ", cpu_pcnt
            print "memory_pcnt = ", memory_pcnt
            print "memory_used = ", memory_used
            print "memory_total = ", memory_total
            print "storage_pcnt = ", storage_pcnt
            print "storage_used = ", storage_used
            print "storage_total = ", storage_total
        
            print "---------------------------------"
        
            self.label_uptime_value.setText(str(uptime))

            self.pbar_cpu.setFormat(Qt.QString("%v%"))
            self.pbar_cpu.setValue(int(cpu_pcnt))
        
            self.pbar_memory.setFormat(Qt.QString("%v% [%1 of %2 MiB]").arg(memory_used, memory_total))
            self.pbar_memory.setValue(int(memory_pcnt))
        
            self.pbar_storage.setFormat(Qt.QString("%v% [%1 of %2 GiB]").arg(storage_used, storage_total))
            self.pbar_storage.setValue(int(storage_pcnt))
        
        self.rp.release()
