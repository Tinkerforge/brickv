#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Hex Validator for Tinkerforge Brickv RS232 Plugin
Copyright (C) 2015 Vincent Szurma <vincent@szurma.de>

TFHexValidator.py: Validator for Hex Inputs
Written for Tinkerforge RS232-Bricklet Brickv-Plugin

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

from PyQt4.QtGui import QValidator
from PyQt4.QtCore import QRegExp

class TFHexValidator(QValidator):
    def __init__(self):
        QValidator.__init__(self)

    def validate(self, _input, _pos):
        re_valid  = QRegExp('^([0-9A-Fa-f]{2})*$')
        re_interm = QRegExp('^([0-9A-Fa-f]{2})*([0-9A-Fa-f]{1})$')

        _input=_input.upper()

        if re_valid.exactMatch(_input):
            return (QValidator.Acceptable, _input, _pos)
        elif re_interm.exactMatch(_input):
            return (QValidator.Intermediate, _input, _pos)

        return (QValidator.Invalid, _input, _pos)


    def fixup(self, _input):
        if len(_input)%2 == 1:
            return _input[:-1]+'0'+ _input[-1:]

        return ''