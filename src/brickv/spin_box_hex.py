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

from PyQt5.QtCore import QRegExp
from PyQt5.QtWidgets import QSpinBox
from PyQt5.QtGui import QRegExpValidator

class SpinBoxHex(QSpinBox):
    def __init__(self, parent=None, default_value=0, digit_block_size=2):
        super().__init__(parent)

        self.validator = QRegExpValidator(QRegExp('^([ ]*[0-9A-Fa-f][ ]*){1,8}$'), self)
        self.digit_block_size = digit_block_size
        self.hex_mode_enabled = True
        self.setValue(default_value)

    def enable_hex_mode(self, digit_block_size=None):
        self.hex_mode_enabled = True
        if digit_block_size is not None:
            self.digit_block_size = digit_block_size
        self.setValue(self.value())

    def disable_hex_mode(self):
        self.hex_mode_enabled = False
        self.setValue(self.value())

    def validate(self, text, pos):
        if not self.hex_mode_enabled:
            return super().validate(text, pos)
        return self.validator.validate(text, pos)

    def valueFromText(self, text):
        if not self.hex_mode_enabled:
            return super().valueFromText(text)
        return min(int(text.replace(' ', ''), 16), self.maximum())

    def textFromValue(self, value):
        if not self.hex_mode_enabled:
            return super().textFromValue(value)
        rev_text = hex(value).replace('0x', '').upper()[::-1]
        blocks = [rev_text[i:i+self.digit_block_size] for i in range(0, len(rev_text), self.digit_block_size)]

        # Reverse blocks and chars in block to undo reverse on the string above
        text = ' '.join(s[::-1] for s in blocks[::-1])
        if len(blocks[0]) != self.digit_block_size:
            text = '0' * (self.digit_block_size - len(blocks[0])) + text
        return text
