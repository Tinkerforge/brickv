# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2013-2015 Matthias Bolte <matthias@tinkerforge.com>
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

load_pixmap.py: Functions to load (frozen) images and optionally convert it to alpha channel pixmap

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

import os
import sys

from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import Qt, QByteArray

from brickv.utils import get_resources_path


def load_pixmap(path):
    absolute_path = get_resources_path(path)
    pixmap = QPixmap(absolute_path)

    return pixmap

def load_masked_pixmap(path):
    pixmap = load_pixmap(path)
    mask = pixmap.createMaskFromColor(QColor(0xFF, 0x00, 0xF0), Qt.MaskInColor)
    pixmap.setMask(mask)

    return pixmap
