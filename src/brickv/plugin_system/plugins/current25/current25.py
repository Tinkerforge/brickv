# -*- coding: utf-8 -*-
"""
Current25 Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

current25.py: Current25 Plugin Implementation

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

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QPushButton, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings import ip_connection
from brickv.bindings.bricklet_current25 import BrickletCurrent25
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_current

class Current25(PluginBase):
    qtcb_over = pyqtSignal()

    def __init__(self, *args):
        PluginBase.__init__(self, BrickletCurrent25, *args)

        self.cur = self.device

        self.cbe_current = CallbackEmulator(self.cur.get_current,
                                            self.cb_current,
                                            self.increase_error_count)

        self.qtcb_over.connect(self.cb_over)
        self.cur.register_callback(self.cur.CALLBACK_OVER_CURRENT,
                                   self.qtcb_over.emit)

        self.over_label = QLabel('Over Current: No')
        self.calibrate_button = QPushButton('Calibrate Zero')
        self.calibrate_button.clicked.connect(self.calibrate_clicked)

        self.current_current = None # float, A

        plots = [('Current', Qt.red, lambda: self.current_current, format_current)]
        self.plot_widget = PlotWidget('Current [A]', plots, extra_key_widgets=[self.over_label])

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addWidget(self.calibrate_button)

    def start(self):
        async_call(self.cur.get_current, None, self.cb_current, self.increase_error_count)
        self.cbe_current.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_current.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCurrent25.DEVICE_IDENTIFIER

    def cb_current(self, current):
        self.current_current = current / 1000.0

    def cb_over(self):
        self.over_label.setText('Over Current: Yes')

    def calibrate_clicked(self):
        try:
            self.cur.calibrate()
        except ip_connection.Error:
            return
