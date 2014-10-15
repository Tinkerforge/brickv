# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_settings.py: RED settings tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings
from brickv.plugin_system.plugins.red.api import *
from brickv.plugin_system.plugins.red import config_parser

from brickv.async_call import async_call

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    script_manager = None
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None
        self.brickd_conf = None

    def tab_on_focus(self):
        self.brickd_conf = REDFile(self.session)
        async_call(self.brickd_conf.open, ('/etc/brickd.conf', REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0), self.cb_brickd_conf_open, self.cb_brickd_conf_open_error)

    def tab_off_focus(self):
        pass

    # the callbacks
    def cb_brickd_conf_open_error(self):
        print "Could not open brickd.conf"
        
    def cb_brickd_conf_open(self, result):
        self.brickd_conf.read_async(4096, self.cb_read_brickd_conf)
        
    def cb_read_brickd_conf(self, result):
        if result == None:
            print "Could not read brickd.conf"
            
        print config_parser.parse(result.data)
        self.brickd_conf.release()
