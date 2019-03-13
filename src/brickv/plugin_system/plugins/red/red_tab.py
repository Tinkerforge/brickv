# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab.py: RED tab implementation

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

from PyQt5.QtWidgets import QWidget

class REDTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(self, parent)

        # will be set from RED after construction
        self.session        = None
        self.script_manager = None
        self.image_version  = None

    def tab_on_focus(self):
        raise NotImplementedError()

    def tab_off_focus(self):
        raise NotImplementedError()

    def tab_destroy(self):
        raise NotImplementedError()
