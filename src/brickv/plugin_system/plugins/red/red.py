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
from brickv.plugin_system.plugins.red.api import REDError, REDString, REDFile, REDProcess

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
        f1 = REDFile(self.red).open('/tmp/blubb123', REDFile.FLAG_WRITE_ONLY | REDFile.FLAG_CREATE | REDFile.FLAG_NON_BLOCKING | REDFile.FLAG_TRUNCATE, 0755, 0, 0)
        f1.write('foobar1 foobar2 foobar3 foobar4 foobar5 foobar6')
        f1.release()

        f2 = REDFile(self.red).open('/tmp/blubb123', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0)
        print 'READ: ' + f2.read(256)
        f2.release()

        sin = REDFile(self.red).open('/dev/null', REDFile.FLAG_READ_ONLY, 0, 0, 0)
        sout = REDFile(self.red).open('/dev/null', REDFile.FLAG_WRITE_ONLY, 0, 0, 0)
        self.p = REDProcess(self.red)
        self.p.state_changed_callback = self.foobar
        self.p.spawn('touch', ['/tmp/fffffffffffffffffffffffffffff'], [], '/', 0, 0, sin, sout, sout)
        print self.p.arguments.items[0].data

    def foobar(self, p):
        print 'foobar', p.state, p.exit_code
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
