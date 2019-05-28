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
    def __init__(self, parent=None):
        super().__init__(parent)
        self.leading_zeros = 6

    def use_leading_zeros(self, n):
        self.leading_zeros = n
        self.setValue(self.value())

    def textFromValue(self, value):
        return '{{:0{}d}}'.format(self.leading_zeros).format(value)

    def valueFromText(self, text):
        return int(text, 10)
