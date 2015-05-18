# -*- coding: utf-8 -*-
"""
CO2 Bricklet Plugin
Copyright (C) 2015 Olaf Lüke <olaf@tinkerforge.com>

co2.py: CO2 Bricklet Plugin Implementation

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
from PyQt4.QtGui import QVBoxLayout, QLabel, QHBoxLayout

from brickv.plugin_system.plugin_base import PluginBase
from brickv.bindings.bricklet_co2 import BrickletCO2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class CO2ConcentrationLabel(QLabel):
    def setText(self, text):
        text = "CO2 Concentration: " + text + " ppm (parts per million)"
        super(CO2ConcentrationLabel, self).setText(text)

class CO2(PluginBase):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletCO2, *args)

        self.co2 = self.device

        self.cbe_co2_concentration = CallbackEmulator(self.co2.get_co2_concentration,
                                                      self.cb_co2_concentration,
                                                      self.increase_error_count)

        self.co2_concentration_label = CO2ConcentrationLabel('CO2 Concentration: ')

        self.current_value = None

        plot_list = [['', Qt.red, self.get_current_value]]
        self.plot_widget = PlotWidget('CO2 Concentration [ppm]', plot_list)

        layout_h2 = QHBoxLayout()
        layout_h2.addStretch()
        layout_h2.addWidget(self.co2_concentration_label)
        layout_h2.addStretch()

        layout = QVBoxLayout(self)
        layout.addLayout(layout_h2)
        layout.addWidget(self.plot_widget)

    def start(self):
        async_call(self.co2.get_co2_concentration, None, self.cb_co2_concentration, self.increase_error_count)
        self.cbe_co2_concentration.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_co2_concentration.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    def get_url_part(self):
        return 'co2'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletCO2.DEVICE_IDENTIFIER

    def get_current_value(self):
        return self.current_value

    def cb_co2_concentration(self, co2_concentration):
        self.current_value = co2_concentration
        self.co2_concentration_label.setText(str(co2_concentration))
