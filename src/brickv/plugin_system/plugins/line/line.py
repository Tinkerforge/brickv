# -*- coding: utf-8 -*-
"""
Line Plugin
Copyright (C) 2013 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QLabel, QHBoxLayout, QFrame, QPainter, QLinearGradient

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_line import BrickletLine
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class ReflectivityFrame(QFrame):
    def __init__(self, parent=None):
        QFrame.__init__(self, parent)
        self.reflectivity = 0
        self.setMinimumSize(150, 150)

    def set_reflectivity(self, reflectivity):
        self.reflectivity = reflectivity
        self.update()

    def paintEvent(self, event):
        qp = QPainter(self)

        g = QLinearGradient(0.0, 0.0, 0.0, self.height())
        g.setColorAt(0, Qt.white)
        g.setColorAt(1, Qt.black)

        y = self.height() - self.reflectivity * self.height() / 4095.0

        qp.fillRect(0, 0, self.width(), self.height(), g)
        qp.setPen(Qt.red)
        qp.drawLine(0, y, self.width(), y)

class Line(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletLine, *args)

        self.line = self.device

        self.cbe_reflectivity = CallbackEmulator(self.line.get_reflectivity,
                                                 self.cb_reflectivity,
                                                 self.increase_error_count)

        self.rf = ReflectivityFrame()

        self.current_reflectivity = None

        plots = [('Reflectivity', Qt.red, lambda: self.current_reflectivity, str)]
        self.plot_widget = PlotWidget('Reflectivity', plots)

        layout = QHBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(self.rf)

    def cb_reflectivity(self, reflectivity):
        self.current_reflectivity = reflectivity
        self.rf.set_reflectivity(reflectivity)

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
