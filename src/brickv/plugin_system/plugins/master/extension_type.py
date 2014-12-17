# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2012-2014 Matthias Bolte <matthias@tinkerforge.com>

extension_type.py: ExtensionType for Master Plugin implementation

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

from PyQt4.QtGui import QFrame, QMessageBox
from PyQt4.QtCore import Qt

from brickv.plugin_system.plugins.master.ui_extension_type import Ui_extension_type
from brickv.async_call import async_call
from brickv.utils import get_main_window

class ExtensionType(QFrame, Ui_extension_type):
    def __init__(self, parent):
        QFrame.__init__(self, parent, Qt.Popup | Qt.Window | Qt.Tool)

        self.setupUi(self)

        self.setWindowTitle("Configure Extension Type")

        self.parent = parent
        self.master = parent.master
        self.button_type_save.clicked.connect(self.save_clicked)
        self.combo_extension.currentIndexChanged.connect(self.index_changed)

        self.index_changed(0)

    def popup_ok(self):
        QMessageBox.information(get_main_window(), "Extension Type", "Successfully saved extension type", QMessageBox.Ok)

    def popup_fail(self):
        QMessageBox.critical(get_main_window(), "Extension Type", "Could not save extension type", QMessageBox.Ok)

    def index_changed_async(self, ext):
        if ext < 0 or ext > (self.type_box.count() - 1):
            ext = 0
        self.type_box.setCurrentIndex(ext)

    def index_changed(self, index):
        async_call(self.master.get_extension_type, index, self.index_changed_async, self.parent.increase_error_count)

    def save_clicked(self):
        extension = self.combo_extension.currentIndex()
        typ = self.type_box.currentIndex()
        try:
            self.master.set_extension_type(extension, typ)
        except:
            self.popup_fail()
            return

        try:
            new_type = self.master.get_extension_type(extension)
        except:
            self.popup_fail()
            return

        if typ == new_type:
            self.popup_ok()
        else:
            self.popup_fail()
