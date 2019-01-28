# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

leading_zero_spin_box.py: LeadingZeroSpinBox implementation

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

from PyQt5.QtWidgets import QSpinBox

class LeadingZeroSpinBox(QSpinBox):
    def valueFromText(self, text):
        return int(text, 10)

    def textFromValue(self, value):
        if value < 0:
            return str(value)
        else:
            return '%02d' % value
