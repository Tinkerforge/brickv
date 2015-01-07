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

from brickv.plugin_system.plugins.red.red_tab import REDTab
from brickv.plugin_system.plugins.red.ui_red_tab_settings import Ui_REDTabSettings

class REDTabSettings(REDTab, Ui_REDTabSettings):
    def __init__(self):
        REDTab.__init__(self)

        self.setupUi(self)

        self.tabs = []

        for i in range(self.tab_widget.count()):
            self.tabs.append(self.tab_widget.widget(i))

        self.tab_widget.currentChanged.connect(self.tab_widget_current_changed)

    def tab_on_focus(self):
        for tab in self.tabs:
            tab.session           = self.session
            tab.script_manager    = self.script_manager
            tab.image_version_ref = self.image_version_ref

        self.tab_widget.currentWidget().tab_on_focus()

    def tab_off_focus(self):
        for tab in self.tabs:
            tab.tab_off_focus()

    def tab_destroy(self):
        pass

    def tab_widget_current_changed(self, index):
        for i, tab in enumerate(self.tabs):
            if i == index:
                tab.tab_on_focus()
            else:
                tab.tab_off_focus()
