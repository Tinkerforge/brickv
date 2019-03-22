# -*- coding: utf-8 -*-
"""
Ozone Bricklet Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2016 Matthias Bolte <matthias@tinkerforge.com>

ozone.py: Ozone Bricklet Plugin Implementation

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
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QSpinBox, QFrame, QLabel

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ozone import BrickletOzone
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class Ozone(PluginBase):
    def __init__(self, *args):
        super().__init__(BrickletOzone, *args)

        self.ozone = self.device

        self.cbe_ozone_concentration = CallbackEmulator(self.ozone.get_ozone_concentration,
                                                        self.cb_ozone_concentration,
                                                        self.increase_error_count)

        self.current_ozone_concentration = None

        plots = [('Ozone Concentration', Qt.red, lambda: self.current_ozone_concentration, '{} ppb'.format)]
        self.plot_widget = PlotWidget('Ozone Concentration [ppb]', plots, y_resolution=1.0)

        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)

        hlayout = QHBoxLayout()
        hlayout.addWidget(QLabel('Moving Average Length:'))
        hlayout.addWidget(self.spin_average)
        hlayout.addStretch()

        line = QFrame()
        line.setObjectName("line")
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)

        layout = QVBoxLayout(self)
        layout.addWidget(self.plot_widget)
        layout.addWidget(line)
        layout.addLayout(hlayout)

    def get_moving_average_async(self, average):
        self.spin_average.setValue(average)

    def start(self):
        async_call(self.ozone.get_moving_average, None, self.get_moving_average_async, self.increase_error_count)
        async_call(self.ozone.get_ozone_concentration, None, self.cb_ozone_concentration, self.increase_error_count)
        self.cbe_ozone_concentration.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_ozone_concentration.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletOzone.DEVICE_IDENTIFIER

    def cb_ozone_concentration(self, ozone_concentration):
        self.current_ozone_concentration = ozone_concentration

    def spin_average_finished(self):
        self.ozone.set_moving_average(self.spin_average.value())
