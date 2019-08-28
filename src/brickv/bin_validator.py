#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

bin_validator.py: Validator for Binary Inputs

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
from PyQt5.QtCore import QRegularExpression

class BinValidator(QValidator):
    def __init__(self, max_bits=-1, bit_group_size=4):
        super().__init__()

        self.max_bits = max_bits
        self.bit_group_size = bit_group_size

        if max_bits == 0:
            self.re_acceptable = QRegularExpression('')
        elif max_bits > 0:
            self.re_acceptable = QRegularExpression('^([0,1,\\s]){0,%d}$' % (max_bits))
        else:
            self.re_acceptable = QRegularExpression('^([0,1,\\s])*$')

    def validate(self, text, _pos):
        text = text.upper()

        if self.re_acceptable.match(text).hasMatch():
            return QValidator.Acceptable, text, _pos

        return QValidator.Invalid, text, _pos

    def fixup(self, text):
        text = text.replace(' ', '')
        return ' '.join([text[i:i+self.bit_group_size] for i in range(0, len(text), self.bit_group_size)])
