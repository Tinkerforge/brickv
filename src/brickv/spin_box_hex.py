# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

spin_box_hex.py: SpinBoxHex implementation

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

from PyQt4.QtCore import QRegExp
from PyQt4.QtGui import QSpinBox, QRegExpValidator

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None, default_value=0):
        QSpinBox.__init__(self, parent)

        self.validator = QRegExpValidator(QRegExp('^([ ]*[0-9A-Fa-f][ ]*){1,8}$'), self)
        self.setValue(default_value)

    def validate(self, text, pos):
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        return min(int(text.replace(' ', ''), 16), (1 << 31) - 1)

    def textFromValue(self, value):
        s = ''

        for i, c in enumerate(reversed(hex(value).replace('0x', '').upper())):
            if i % 2 == 0:
                s = ' ' + s

            s = c + s

        s = s.strip()

        if len(s.replace(' ', '')) % 2 == 1:
            s = '0' + s

        return s
