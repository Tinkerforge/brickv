# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2020 Matthias Bolte <matthias@tinkerforge.com>

fixed_size_label.py: QLabel that can only grow

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

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QLabel

class FixedSizeLabel(QLabel):
    maximum_size_hint = None

    def sizeHint(self):
        hint = QLabel.sizeHint(self)

        if self.maximum_size_hint != None:
            hint = QSize(max(hint.width(), self.maximum_size_hint.width()),
                         max(hint.height(), self.maximum_size_hint.height()))

        self.maximum_size_hint = hint

        return hint
