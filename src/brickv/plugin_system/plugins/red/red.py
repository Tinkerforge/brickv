# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

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
from brickv.plugin_system.plugins.red.api import REDError, REDInventory, REDString, REDFile, REDPipe, REDDirectory, REDProcess

class RED(PluginBase, Ui_RED):
    def __init__(self, *args):
        PluginBase.__init__(self, 'RED Brick', BrickRED, *args)

        self.setupUi(self)

        self.red = self.device

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

        self.p.state_changed_callback = self.foobar
        self.p.spawn('/tmp/print', ['fffffffffffffffffffffffffffff'], [], '/', 0, 0, sin, sout, sout)

        tmp = REDDirectory(self.red).open('/tmp')

        for entry in tmp.entries:
            print entry

    def foobar(self, p):
        print 'foobar', p.state, p.timestamp, p.pid, p.exit_code
        print 'echo: ' + self.p.stdout.read(256)
        self.p = None
        """

    def start(self):
        pass

    def stop(self):
        pass

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
