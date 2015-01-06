# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

spin_box_hex.py: SpinBoxHex for Master Plugin implementation

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

from PyQt4.QtGui import QSpinBox, QRegExpValidator
from PyQt4.QtCore import QRegExp

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None):
        super(SpinBoxHex, self).__init__(parent)

        self.validator = QRegExpValidator(QRegExp("[0-9A-Fa-f]{1,2}"), self)
        self.setRange(0, 255)

    def fixCase(self, text):
        self.lineEdit().setText(text.toUpper())

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return int(text, 16)

    def textFromValue(self, value):
        s = hex(value).replace('0x', '').upper()

        if len(s) == 1:
            s = '0' + s

        return s
