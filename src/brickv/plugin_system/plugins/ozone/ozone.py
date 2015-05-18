# -*- coding: utf-8 -*-
"""
Ozone Bricklet Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt4.QtCore import Qt
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout, QSpinBox

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_ozone import BrickletOzone
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class OzoneConcentrationLabel(QLabel):
    def setText(self, text):
        text = "Ozone Concentration: " + text + " ppb (parts per billion)"
        super(OzoneConcentrationLabel, self).setText(text)

class Ozone(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletOzone, *args)

        self.ozone = self.device

        self.cbe_ozone_concentration = CallbackEmulator(self.ozone.get_ozone_concentration,
                                                        self.cb_ozone_concentration,
                                                        self.increase_error_count)

        self.ozone_concentration_label = OzoneConcentrationLabel('Ozone Concentration: ')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('Ozone Concentration [ppb]', plot_list)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.ozone_concentration_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

        self.spin_average = QSpinBox()
        self.spin_average.setMinimum(1)
        self.spin_average.setMaximum(50)
        self.spin_average.setSingleStep(1)
        self.spin_average.setValue(50)
        self.spin_average.editingFinished.connect(self.spin_average_finished)

        layout_h1 = QHBoxLayout()
        layout_h1.addWidget(QLabel('Length of moving average:'))
        layout_h1.addWidget(self.spin_average)
        layout_h1.addStretch()
        layout.addLayout(layout_h1)

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

    def get_url_part(self):
        return 'ozone'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletOzone.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_ozone_concentration(self, ozone_concentration):
        self.current_value = ozone_concentration
        self.ozone_concentration_label.setText(str(ozone_concentration))

    def spin_average_finished(self):
        self.ozone.set_moving_average(self.spin_average.value())
