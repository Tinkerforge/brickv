# -*- coding: utf-8 -*-
"""
Analog In 2.0 Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2015-2016 Matthias Bolte <matthias@tinkerforge.com>

analog_in_v2.py: Analog In 2.0 Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_analog_in_v2 import BrickletAnalogInV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_voltage

class AnalogInV2(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletAnalogInV2, *args)

        self.ai = self.device

        self.cbe_voltage = CallbackEmulator(self.ai.get_voltage,
                                            self.cb_voltage,
                                            self.increase_error_count)

        self.current_voltage = None # float, V

        plots = [('Voltage', Qt.red, lambda: self.current_voltage, format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots)

        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(QLabel('Moving Average Length:'))
        layout_h1.addWidget(self.spin_average)
        layout_h1.addStretch()

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(layout_h1)

    def get_moving_average_async(self, average):
        self.spin_average.setValue(average)

    def start(self):
        async_call(self.ai.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.ai.get_voltage, None, self.cb_voltage, self.increase_error_count)
        self.cbe_voltage.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_voltage.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogInV2.DEVICE_IDENTIFIER

    def cb_voltage(self, voltage):
        self.current_voltage = voltage / 1000.0

    def spin_average_finished(self):
        self.ai.set_moving_average(self.spin_average.value())
