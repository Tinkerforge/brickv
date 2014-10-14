# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>

red_tab_extension.py: RED extension configuration

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
from brickv.plugin_system.plugins.red.ui_red_tab_extension import Ui_REDTabExtension
from brickv.plugin_system.plugins.red.api import *

from brickv.plugin_system.plugins.red.script_manager import ScriptManager
from brickv.async_call import async_call

class REDTabExtension(QtGui.QWidget, Ui_REDTabExtension):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None
        self.red_file = [None, None]
        
    def status(self, i, j):
        print i, j
        
    def cb_file_read(self, extension, result):
        print extension

        if result.error == None:
            string = str(bytearray(result.data))
            print string
        
        self.red_file[extension].release()
        
    def cb_file_open_error(self, extension):
        print "extension", extension, "not present"
#        self.red_file[extension].release()
        
    def cb_file_open(self, extension, result):
        print result
        if not isinstance(result, REDFile):
            return
        
        
        self.red_file[extension] = result
        self.red_file[extension].read_async(self.red_file[extension].length, lambda x: self.cb_file_read(0, x), self.status)
        
    def tab_on_focus(self):
        self.red_file[0] = REDFile(self.session)
        async_call(self.red_file[0].open, ("/tmp/extension_position_0.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0), lambda x: self.cb_file_open(0, x), lambda: self.cb_file_open_error(0))
#        self.red_file0.read_async(self.red_file0.length, lambda x: self.cb(0, x), self.status)

        self.red_file[1] = REDFile(self.session)
        async_call(self.red_file[1].open, ("/tmp/extension_position_1.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0), lambda x: self.cb_file_open(1, x), lambda: self.cb_file_open_error(1))
        
#        self.red_file1 = REDFile(self.session).open("/tmp/extension_position_1.conf", REDFile.FLAG_READ_ONLY | REDFile.FLAG_NON_BLOCKING, 0, 0, 0)
#        self.red_file1.read_async(self.red_file1.length, lambda x: self.cb(0, x), self.status)

    def tab_off_focus(self):
        pass
