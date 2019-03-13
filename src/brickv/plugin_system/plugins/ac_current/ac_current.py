# -*- coding: utf-8 -*-
"""
AC Current Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

ac_current.py: AC Current Plugin Implementation

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

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QComboBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ac_current import BrickletACCurrent
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_current

class ACCurrent(PluginBase):
    def __init__(self, *args):
        super().__init__(self, BrickletACCurrent, *args)

        self.acc = self.device

        self.cbe_current = CallbackEmulator(self.acc.get_current,
                                            self.cb_current,
                                            self.increase_error_count)

        self.current_current = None # float, A

        plots = [('Current', Qt.red, lambda: self.current_current, format_current)]
        self.plot_widget = PlotWidget('Current [A]', plots)

        self.label_average = QLabel('Moving Average Length:')
        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)

        self.label_range = QLabel('Current Range:')
        self.combo_range = QComboBox()
        self.combo_range.addItem("0") # TODO: Adjust ranges
        self.combo_range.addItem("1")
        self.combo_range.currentIndexChanged.connect(self.new_config)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.label_average)
        hlayout.addWidget(self.spin_average)
        hlayout.addStretch()
        hlayout.addWidget(self.label_range)
        hlayout.addWidget(self.combo_range)

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def get_configuration_async(self, conf):
        self.combo_range.setCurrentIndex(conf)

    def get_moving_average_async(self, average):
        self.spin_average.setValue(average)

    def new_config(self, value):
        try:
            self.acc.set_configuration(value)
        except:
            pass

    def start(self):
        async_call(self.acc.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.acc.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.acc.get_current, None, self.cb_current, self.increase_error_count)
        self.cbe_current.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_current.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletACCurrent.DEVICE_IDENTIFIER

    def cb_current(self, current):
        self.current_current = current / 1000.0

    def spin_average_finished(self):
        self.acc.set_moving_average(self.spin_average.value())
