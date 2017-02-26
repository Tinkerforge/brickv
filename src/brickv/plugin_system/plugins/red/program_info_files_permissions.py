# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2016-2017 Matthias Bolte <matthias@tinkerforge.com>

program_info_files_permissions.py: Program Files Permissions Info Widget

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDialog

from brickv.plugin_system.plugins.red.ui_program_info_files_permissions import Ui_ProgramInfoFilesPermissions

class ProgramInfoFilesPermissions(QDialog, Ui_ProgramInfoFilesPermissions):
    def __init__(self, parent, title, permissions):
        QDialog.__init__(self, parent)

        self.setupUi(self)
        self.setModal(True)
        self.setWindowTitle(title)

        self.button_okay.clicked.connect(self.accept)
        self.button_cancel.clicked.connect(self.reject)

        self.check_owner_read.setChecked(permissions & 0o400)
        self.check_owner_write.setChecked(permissions & 0o200)
        self.check_owner_execute.setChecked(permissions & 0o100)

        self.check_group_read.setChecked(permissions & 0o40)
        self.check_group_write.setChecked(permissions & 0o20)
        self.check_group_execute.setChecked(permissions & 0o10)

        self.check_other_read.setChecked(permissions & 0o4)
        self.check_other_write.setChecked(permissions & 0o2)
        self.check_other_execute.setChecked(permissions & 0o1)

    def get_permissions(self):
        permissions = 0

        if self.check_owner_read.isChecked():
            permissions |= 0o400

        if self.check_owner_write.isChecked():
            permissions |= 0o200

        if self.check_owner_execute.isChecked():
            permissions |= 0o100

        if self.check_group_read.isChecked():
            permissions |= 0o40

        if self.check_group_write.isChecked():
            permissions |= 0o20

        if self.check_group_execute.isChecked():
            permissions |= 0o10

        if self.check_other_read.isChecked():
            permissions |= 0o4

        if self.check_other_write.isChecked():
            permissions |= 0o2

        if self.check_other_execute.isChecked():
            permissions |= 0o1

        return permissions
