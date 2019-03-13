# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2010 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014 Matthias Bolte <matthias@tinkerforge.com>

speedometer.py: TODO

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

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from PyQt5.QtCore import Qt

from brickv.knob_widget import KnobWidget

class SpeedoMeter(QWidget):
    def __init__(self, *args):
        super().__init__(self, *args)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.knob = KnobWidget()
        self.knob.setFocusPolicy(Qt.NoFocus)
        self.knob.set_total_angle(280)
        self.knob.set_range(0, 0x7FFF)
        self.knob.set_scale(5000, 2)
        self.knob.set_scale_arc_visible(False)
        self.knob.set_knob_radius(60)
        self.knob.set_knob_style(KnobWidget.STYLE_NEEDLE)
        self.knob.set_value(0)
        self.knob.set_title_text('Standstill')
        self.knob.set_dynamic_resize_enabled(True)

        layout.addWidget(self.knob)

    def set_velocity(self, value):
        if value == self.knob.get_value():
            return

        if value > 0:
            self.knob.set_title_text('Forward')
        elif value < 0:
            self.knob.set_title_text('Backward')
        else:
            self.knob.set_title_text('Standstill')

        if value < 0:
            value = -value

        self.knob.set_value(value)
