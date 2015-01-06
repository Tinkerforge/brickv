# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>
Copyright (C) 2014 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

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
from brickv.utils import get_main_window

# Indexes
BOX_INDEX_NETWORK = 0
BOX_INDEX_BRICKD = 1
BOX_INDEX_DATETIME = 2
BOX_INDEX_FILESYSTEM = 3
BOX_INDEX_SERVICES = 4

class REDTabSettings(QtGui.QWidget, Ui_REDTabSettings):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setupUi(self)

        self.session        = None # set from RED after construction
        self.script_manager = None # set from RED after construction

        self.is_tab_on_focus = False

        self.tab_list = []

        for i in range(self.tab_widget.count()):
            self.tab_list.append(self.tab_widget.widget(i))

        # Boxes
        self.tab_widget.currentChanged.connect(self.slot_tab_widget_current_changed)

    def tab_on_focus(self):
        self.is_tab_on_focus = True

        for tab in self.tab_list:
            tab.session = self.session
            tab.script_manager = self.script_manager

        self.tab_widget.currentWidget().tab_on_focus()

    def tab_off_focus(self):
        self.is_tab_on_focus = False

        for tab in self.tab_list:
            tab.tab_off_focus()

    def tab_destroy(self):
        pass

    def slot_tab_widget_current_changed(self, ctidx):
        for i in range(self.tab_widget.count()):
            if i == ctidx:
                self.tab_list[i].tab_on_focus()
            else:
                self.tab_list[i].tab_off_focus()
