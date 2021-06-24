# -*- coding: utf-8 -*-
"""
Analog In Plugin
Copyright (C) 2011-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

analog_in.py: Analog In Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QLabel, QHBoxLayout, QComboBox, QSpinBox, QFrame

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_analog_in import BrickletAnalogIn
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_voltage

class AnalogIn(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletAnalogIn, *args)

        self.ai = self.device

        # the firmware version of a EEPROM Bricklet can (under common circumstances)
        # not change during the lifetime of an EEPROM Bricklet plugin. therefore,
        # it's okay to make final decisions based on it here
        self.has_range = self.firmware_version >= (2, 0, 1)
        self.has_averaging = self.firmware_version >= (2, 0, 3)

        self.cbe_voltage = CallbackEmulator(self,
                                            self.ai.get_voltage,
                                            None,
                                            self.cb_voltage,
                                            self.increase_error_count)

        self.current_voltage = CurveValueWrapper() # float, V

        plots = [('Voltage', Qt.red, self.current_voltage, format_voltage)]
        self.plot_widget = PlotWidget('Voltage [V]', plots, y_resolution=0.001)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)

        if self.has_range:
            self.combo_range = QComboBox()
            self.combo_range.addItem('Automatic', BrickletAnalogIn.RANGE_AUTOMATIC)

            if self.has_averaging:
                self.combo_range.addItem('0 - 3.30 V', BrickletAnalogIn.RANGE_UP_TO_3V)

            self.combo_range.addItem('0 - 6.05 V', BrickletAnalogIn.RANGE_UP_TO_6V)
            self.combo_range.addItem('0 - 10.32 V', BrickletAnalogIn.RANGE_UP_TO_10V)
            self.combo_range.addItem('0 - 36.30 V', BrickletAnalogIn.RANGE_UP_TO_36V)
            self.combo_range.addItem('0 - 45.00 V', BrickletAnalogIn.RANGE_UP_TO_45V)
            self.combo_range.currentIndexChanged.connect(self.range_changed)

            hlayout = QHBoxLayout()
            hlayout.addWidget(QLabel('Range:'))
            hlayout.addWidget(self.combo_range)
            hlayout.addStretch()

            if self.has_averaging:
                self.spin_average = QSpinBox()
                self.spin_average.setMinimum(0)
                self.spin_average.setMaximum(255)
                self.spin_average.setSingleStep(1)
                self.spin_average.setValue(50)
                self.spin_average.editingFinished.connect(self.spin_average_finished)

                hlayout.addWidget(QLabel('Average Length:'))
                hlayout.addWidget(self.spin_average)

            line = QFrame()
            line.setObjectName("line")
            line.setFrameShape(QFrame.HLine)
            line.setFrameShadow(QFrame.Sunken)

            layout.addWidget(line)
            layout.addLayout(hlayout)

    def get_range_async(self, range_):
        self.combo_range.setCurrentIndex(self.combo_range.findData(range_))

    def get_averaging_async(self, average):
        self.spin_average.setValue(average)

    def start(self):
        if self.has_range:
            async_call(self.ai.get_range, None, self.get_range_async, self.increase_error_count)

        if self.has_averaging:
            async_call(self.ai.get_averaging, None, self.get_averaging_async, self.increase_error_count)

        self.cbe_voltage.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_voltage.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletAnalogIn.DEVICE_IDENTIFIER

    def cb_voltage(self, voltage):
        self.current_voltage.value = voltage / 1000.0

    def range_changed(self, index):
        if index >= 0 and self.has_range:
            range_ = self.combo_range.itemData(index)
            async_call(self.ai.set_range, range_, None, self.increase_error_count)

    def spin_average_finished(self):
        self.ai.set_averaging(self.spin_average.value())
