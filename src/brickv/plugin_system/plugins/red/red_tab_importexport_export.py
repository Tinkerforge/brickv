# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2015 Matthias Bolte <matthias@tinkerforge.com>

red_tab_importexport_export.py: RED import/export export tab implementation

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

from PyQt4.QtGui import QWidget
from brickv.plugin_system.plugins.red.ui_red_tab_importexport_export import Ui_REDTabImportExportExport
from brickv.plugin_system.plugins.red.api import *

class REDTabImportExportExport(QWidget, Ui_REDTabImportExportExport):
    def __init__(self):
        QWidget.__init__(self)

        self.setupUi(self)

        self.session        = None # Set from REDTabImportExport
        self.script_manager = None # Set from REDTabImportExport

    def tab_on_focus(self):
        pass

    def tab_off_focus(self):
        pass

    def tab_destroy(self):
        pass
