# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red.py: RED Plugin implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.brick_red import BrickRED
from brickv.async_call import async_call

from brickv.plugin_system.plugins.red.ui_red import Ui_RED
from brickv.plugin_system.plugins.red.red_tab_overview import REDTabOverview
from brickv.plugin_system.plugins.red.api import REDError, REDString, REDFile, REDPipe, REDDirectory, REDProcess, get_processes
from brickv.plugin_system.plugins.red.script_manager import ScriptManager 

class RED(PluginBase, Ui_RED):
    def __init__(self, *args):
        PluginBase.__init__(self, 'RED Brick', BrickRED, *args)
        ScriptManager.red = self.device

        self.setupUi(self)

        self.red = self.device

        self.tabs_list = []
        for index in range(0, self.red_tab_widget.count()):
            self.tabs_list.append(self.red_tab_widget.widget(index))
            self.tabs_list[index].red = self.red

        # signals and slots
        self.red_tab_widget.currentChanged.connect(self.cb_red_tab_widget_current_changed)

        # FIXME: RED Brick doesn't do enumerate-connected callback correctly yet
        #        for Brick(let)s connected to it. Trigger a enumerate to pick up
        #        all devices connected to a RED Brick properly
        self.ipcon.enumerate()

        """
        s1 = REDString(self.red).allocate('a23456789_b23456789_c23456789_d23456789_e23456789_f23456789_g23456789_h23456789_i23456789_j23456789_k')
        print s1

        f1 = REDFile(self.red).open('/tmp/blubb123', REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
        f1.write('foobar1 foobar2 foobar3 foobar4 foobar5 foobar6')
        f1.release()

        f2 = REDFile(self.red).open('/tmp/blubb123', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0)
        print 'READ: ' + f2.read(256)
        f2.release()

        sin = REDFile(self.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
        sout = REDPipe(self.red).create(REDPipe.FLAG_NON_BLOCKING_READ)
        #sout = REDFile(self.red).open('/tmp/fffffffffffffffffffffffffffff.log', REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_TRUNCATE , 0755, 0, 0)
        self.p = REDProcess(self.red)

        self.p.state_changed_callback = self.cb_foobar
        self.p.spawn('/tmp/print', ['fffffffffffffffffffffffffffff'], [], '/', 0, 0, sin, sout, sout)

        tmp = REDDirectory(self.red).open('/tmp')

        for entry in tmp.entries:
            print entry
        """

    def start(self):
        for index, tab in enumerate(self.tabs_list):
            if index == self.red_tab_widget.currentIndex():
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()

    def stop(self):
        for tab in self.tabs_list:
            tab.tab_off_focus()

    def destroy(self):
        pass

    def has_reset_device(self):
        return False # FIXME: will have reboot, instead of reset

    def reset_device(self):
        pass

    def is_brick(self):
        return True

    def get_url_part(self):
        return 'red'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickRED.DEVICE_IDENTIFIER

    # the callbacks
    def cb_red_tab_widget_current_changed(self, tab_index):
        for index, tab in enumerate(self.tabs_list):
            if (index == tab_index):
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()

    def cb_foobar(self, p):
        print 'cb_foobar', p.state, p.timestamp, p.pid, p.exit_code
        print 'echo: ' + self.p.stdout.read(256)
