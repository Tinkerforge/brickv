# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

red_tab_versions.py: RED versions tab implementation

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
from brickv.plugin_system.plugins.red.ui_red_tab_versions import Ui_REDTabVersions
from brickv.plugin_system.plugins.red.api import *

class REDTabVersions(QtGui.QWidget, Ui_REDTabVersions):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session = None

    def tab_on_focus(self):
        pass

    def tab_off_focus(self):
        pass

    # the callbacks
