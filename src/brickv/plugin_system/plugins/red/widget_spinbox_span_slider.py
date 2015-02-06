# -*- coding: utf-8 -*-
"""
RED Plugin
Copyright (C) 2014 Ishraq Ibne Ashraf <ishraq@tinkerforge.com>

widget_span_slider.py: Custom span slider with spinbox implementation

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

from PyQt4 import Qt, QtCore, QtGui
from brickv.plugin_system.plugins.red.QxtSpanSlider import QxtSpanSlider

class widgetSpinBoxSpanSlider(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent)

        self.span_slider = QxtSpanSlider()
        self.sbox_lower = QtGui.QSpinBox()
        self.sbox_upper = QtGui.QSpinBox()
        self.horizontal_layout = QtGui.QHBoxLayout()
        self.horizontal_layout.addWidget(self.sbox_lower)
        self.horizontal_layout.addWidget(self.span_slider)
        self.horizontal_layout.addWidget(self.sbox_upper)

        # Signal and slots
        self.sbox_lower.valueChanged.connect(self.slot_sbox_lower_value_changed)
        self.sbox_upper.valueChanged.connect(self.slot_sbox_upper_value_changed)
        self.span_slider.lowerPositionChanged.connect(self.slot_span_slider_lower_position_changed)
        self.span_slider.upperPositionChanged.connect(self.slot_span_slider_upper_position_changed)

        self.setLayout(self.horizontal_layout)

    def slot_sbox_lower_value_changed(self, value):
        self.span_slider.setLowerValue(value)

    def slot_sbox_upper_value_changed(self, value):
        self.span_slider.setUpperValue(value)

    def slot_span_slider_lower_position_changed(self, value):
        self.sbox_lower.setValue(value)

    def slot_span_slider_upper_position_changed(self, value):
        self.sbox_upper.setValue(value)
