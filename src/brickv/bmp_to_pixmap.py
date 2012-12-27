# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>

bmp_to_pixmap.py: Function to read bmp and convert it to alpha channel pixmap

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

from PyQt4.QtGui import QPixmap, QColor
from PyQt4.QtCore import Qt

def bmp_to_pixmap(url):
    pixmap = QPixmap(url)
    mask1 = pixmap.createMaskFromColor(QColor(0xFF, 0x00, 0XF0), Qt.MaskInColor)
    pixmap.setMask(mask1)

    return pixmap