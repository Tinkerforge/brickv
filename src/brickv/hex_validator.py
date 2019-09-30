# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2015 Vincent Szurma <vincent@szurma.de>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

hex_validator.py: Validator for Hex Inputs

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

from PyQt5.QtGui import QValidator
from PyQt5.QtCore import QRegExp

class HexValidator(QValidator):
    def __init__(self, max_bytes=-1, digit_group_size=2):
        super().__init__()

        self.max_bytes = max_bytes
        self.digit_group_size = digit_group_size

        if max_bytes == 0:
            self.re_acceptable = QRegExp('')
            self.re_intermediate = QRegExp('')
        elif max_bytes > 0:
            self.re_acceptable = QRegExp('([0-9A-Fa-f]{%d} ){0,%d}[0-9A-Fa-f]{%d}' % (digit_group_size, max_bytes - 1, digit_group_size))
            self.re_intermediate = QRegExp('[ ]*|([ ]*[0-9A-Fa-f][ ]*){1,%d}' % (max_bytes * 2))
        else:
            self.re_acceptable = QRegExp('([0-9A-Fa-f]{%d} )*[0-9A-Fa-f]{%d}' % (digit_group_size, digit_group_size))
            self.re_intermediate = QRegExp('[ ]*|([ ]*[0-9A-Fa-f][ ]*)+')

    def validate(self, _input, _pos):
        _input = _input.upper()

        if self.re_acceptable.exactMatch(_input):
            return QValidator.Acceptable, _input, _pos

        if self.re_intermediate.exactMatch(_input):
            return QValidator.Intermediate, _input, _pos

        return QValidator.Invalid, _input, _pos

    def fixup(self, _input):
        text = _input.replace(' ', '')
        if len(text) == 0:
            return ''

        blocks = [text[i:i+self.digit_group_size] for i in range(0, len(text), self.digit_group_size)]

        last_block = blocks[-1]
        if len(last_block) < self.digit_group_size:
            last_block = '0' * (self.digit_group_size - len(last_block)) + last_block

        return ' '.join(blocks[:-1] + [last_block])
