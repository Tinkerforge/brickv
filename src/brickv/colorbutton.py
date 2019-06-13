# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2019 Erik Fleckstein <erik@tinkerforge.com>

colorbutton.py: Common Color Button

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

from PyQt5.QtGui import QPalette, QPainter
from PyQt5.QtWidgets import QPushButton

from brickv.utils import draw_rect

class ColorButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.on = False

    def initialize(self, brightness_colors, background_color=None, border_color=None, style='rectangular'):
        self.brightness = 0
        self.brightness_colors = brightness_colors
        self.background_color = self.palette().color(QPalette.Background) if background_color is None else background_color
        self.border_color = self.palette().color(QPalette.WindowText) if border_color is None else border_color

        if style in ['rectangular', 'circular']:
            self.style = style
        else:
            raise ValueError("ColorButton style has to be either 'rectangular' or 'circular'")

    def paintEvent(self, _event):
        painter = QPainter(self)
        width = self.width()
        height = self.height()

        if self.on:
            fill_color = self.brightness_colors[self.brightness]
        else:
            fill_color = self.background_color

        if self.style == 'rectangular':
            painter.fillRect(0, 0, width, height, fill_color)
            draw_rect(painter, 0, 0, width, height, 1, self.border_color)
        elif self.style == 'circular':
            painter.setPen(self.border_color)
            painter.setBrush(fill_color)
            painter.drawEllipse(1, 1, width - 2, height - 2)

    def switch_off(self):
        self.on = False
        self.update()

    def switch_on(self, brightness=None):
        self.on = True

        if brightness is not None:
            self.brightness = brightness

        self.update()

    def set_brightness(self, brightness):
        self.brightness = brightness
