# -*- coding: utf-8 -*-
"""
Line Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

line.py: Line Plugin Implementation

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

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget
from brickv.bindings.bricklet_line import BrickletLine
from brickv.async_call import async_call
from brickv.utils import CallbackEmulator

from PyQt4.QtGui import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPainter, QBrush, QLinearGradient
from PyQt4.QtCore import Qt

class ReflectivityLabel(QLabel):
    def setText(self, text):
        text = "Reflectivity: " + text
        super(ReflectivityLabel, self).setText(text)

class ReflectivityFrame(QFrame):
    SIZE_X = 400
    SIZE_Y = 100

    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.reflectivity = 0
        self.setMinimumSize(self.SIZE_X, self.SIZE_Y)
        self.setMaximumSize(self.SIZE_X, self.SIZE_Y)

        self.gradient = QLinearGradient(0.0, 0.0, 0.0, self.SIZE_Y)
        self.gradient.setColorAt(0, Qt.white)
        self.gradient.setColorAt(1, Qt.black)

    def set_reflectivity(self, r):
        self.reflectivity = self.SIZE_Y - r*self.SIZE_Y/4095.0
        self.repaint()

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        qp.setBrush(self.gradient)
        qp.setPen(Qt.transparent)
        qp.drawRect(0, 0, self.SIZE_X, self.SIZE_Y)
        qp.setBrush(QBrush(Qt.red))
        qp.setPen(Qt.red)
        qp.drawLine(0, self.reflectivity, self.SIZE_X, self.reflectivity)
        qp.end()

class Line(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLine, *args)

        self.line = self.device

        self.cbe_reflectivity = CallbackEmulator(self.line.get_reflectivity,
                                                 self.cb_reflectivity,
                                                 self.increase_error_count)

        self.reflectivity_label = ReflectivityLabel()
        self.rf = ReflectivityFrame()

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Reflectivity', plot_list)

        layout_h = QHBoxLayout()
        layout_h.addStretch()
        layout_h.addWidget(self.reflectivity_label)
        layout_h.addStretch()

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.rf)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

    def cb_reflectivity(self, reflectivity):
        self.current_value = reflectivity
        self.rf.set_reflectivity(reflectivity)
        self.reflectivity_label.setText(str(reflectivity))

    def get_current_value(self):
        return self.current_value

    def start(self):
        async_call(self.line.get_reflectivity, None, self.cb_reflectivity, self.increase_error_count)
        self.cbe_reflectivity.set_period(25)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_reflectivity.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'line'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletLine.DEVICE_IDENTIFIER
