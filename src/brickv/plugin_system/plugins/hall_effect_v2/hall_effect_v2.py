# -*- coding: utf-8 -*-
"""
Hall Effect 2.0 Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

hall_effect_v2.py: Hall Effect 2.0 Plugin implementation

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

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_hall_effect_v2 import BrickletHallEffectV2
from brickv.plugin_system.plugins.hall_effect_v2.ui_hall_effect_v2 import Ui_HallEffectV2
from brickv.plot_widget import PlotWidget
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

class HallEffectV2(COMCUPluginBase, Ui_HallEffectV2):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletHallEffectV2, *args)

        self.setupUi(self)

        self.hf = self.device

        self.cbe_magnetic_flux_density = CallbackEmulator(self.hf.get_magnetic_flux_density,
                                                          self.cb_magnetic_flux_density,
                                                          self.increase_error_count)
        self.cbe_counter = CallbackEmulator(lambda: self.hf.get_counter(False),
                                            self.cb_counter,
                                            self.increase_error_count)

        self.current_magnetic_flux_density = None
        plots = [('Magnetic Flux Density', Qt.red, lambda: self.current_magnetic_flux_density, '{} µT'.format)]
        self.plot_widget = PlotWidget('Magnetic Flux Density [µT]', plots, y_resolution=1.0)

        self.button_reset.clicked.connect(self.button_reset_clicked)
        self.spinbox_low.editingFinished.connect(self.new_config)
        self.spinbox_high.editingFinished.connect(self.new_config)
        self.spinbox_debounce.editingFinished.connect(self.new_config)

        self.main_vert_layout.insertWidget(0, self.plot_widget)

    def start(self):
        async_call(self.hf.get_magnetic_flux_density, None, self.cb_magnetic_flux_density, self.increase_error_count)
        async_call(lambda: self.hf.get_counter(False), None, self.cb_counter, self.increase_error_count)
        async_call(self.hf.get_counter_config, None, self.cb_counter_config, self.increase_error_count)
        self.cbe_magnetic_flux_density.set_period(25)
        self.cbe_counter.set_period(100)

        self.plot_widget.stop = False

    def stop(self):
        self.cbe_magnetic_flux_density.set_period(0)
        self.cbe_counter.set_period(0)

        self.plot_widget.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHallEffectV2.DEVICE_IDENTIFIER

    def new_config(self):
        high     = self.spinbox_high.value()
        low      = self.spinbox_low.value()
        debounce = self.spinbox_debounce.value()
        self.hf.set_counter_config(high, low, debounce)

    def button_reset_clicked(self):
        async_call(lambda: self.hf.get_counter(True), None, self.cb_counter, self.increase_error_count)

    def cb_counter_config(self, config):
        self.spinbox_high.setValue(config.high_threshold)
        self.spinbox_low.setValue(config.low_threshold)
        self.spinbox_debounce.setValue(config.debounce)

    def cb_counter(self, count):
        self.label_count.setText(str(count))

    def cb_magnetic_flux_density(self, magnetic_flux_density):
        self.current_magnetic_flux_density = magnetic_flux_density
