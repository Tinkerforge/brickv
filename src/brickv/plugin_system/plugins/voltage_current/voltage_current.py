# -*- coding: utf-8 -*-
"""
Voltage/Current Plugin
Copyright (C) 2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2015 Matthias Bolte <matthias@tinkerforge.com>

voltage_current.py: Voltage/Current Plugin Implementation

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
from PyQt5.QtWidgets import QHBoxLayout

from brickv.bindings.bricklet_voltage_current import BrickletVoltageCurrent
from brickv.plugin_system.plugins.voltage_current.ui_voltage_current import Ui_VoltageCurrent
from brickv.plugin_system.plugin_base import PluginBase
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.utils import format_voltage, format_current

def format_power(value): # float, W
    if abs(value) < 1:
        return str(int(round(value * 1000.0))) + ' mW'
    else:
        return format(value, '.3f') + ' W'

class VoltageCurrent(PluginBase, Ui_VoltageCurrent):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickletVoltageCurrent, *args)

        self.setupUi(self)

        self.vc = self.device

        self.cbe_current = CallbackEmulator(self.vc.get_current,
                                            self.cb_current,
                                            self.increase_error_count)
        self.cbe_voltage = CallbackEmulator(self.vc.get_voltage,
                                            self.cb_voltage,
                                            self.increase_error_count)
        self.cbe_power = CallbackEmulator(self.vc.get_power,
                                          self.cb_power,
                                          self.increase_error_count)

        self.current_voltage = CurveValueWrapper() # float, V
        self.current_current = CurveValueWrapper() # float, A
        self.current_power = CurveValueWrapper() # float, W

        plots_voltage = [('Voltage', Qt.red, self.current_voltage, format_voltage)]
        plots_current = [('Current', Qt.blue, self.current_current, format_current)]
        plots_power = [('Power', Qt.darkGreen, self.current_power, format_power)]
        self.plot_widget_voltage = PlotWidget('Voltage [V]', plots_voltage, clear_button=self.button_clear_graphs, y_resolution=0.001)
        self.plot_widget_current = PlotWidget('Current [A]', plots_current, clear_button=self.button_clear_graphs, y_resolution=0.001)
        self.plot_widget_power = PlotWidget('Power [W]', plots_power, clear_button=self.button_clear_graphs, y_resolution=0.001)

        self.save_cal_button.clicked.connect(self.save_cal_clicked)
        self.save_conf_button.clicked.connect(self.save_conf_clicked)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.plot_widget_voltage)
        hlayout.addWidget(self.plot_widget_current)
        hlayout.addWidget(self.plot_widget_power)

        self.main_layout.insertLayout(0, hlayout)

    def get_configuration_async(self, conf):
        avg, vol, cur = conf
        self.averaging_box.setCurrentIndex(avg)
        self.voltage_box.setCurrentIndex(vol)
        self.current_box.setCurrentIndex(cur)

    def get_calibration_async(self, calibration):
        gainmul, gaindiv = calibration
        self.gainmul_spinbox.setValue(gainmul)
        self.gaindiv_spinbox.setValue(gaindiv)

    def start(self):
        async_call(self.vc.get_configuration, None, self.get_configuration_async, self.increase_error_count)
        async_call(self.vc.get_calibration, None, self.get_calibration_async, self.increase_error_count)

        self.cbe_current.set_period(100)
        self.cbe_voltage.set_period(100)
        self.cbe_power.set_period(100)

        self.plot_widget_current.stop = False
        self.plot_widget_voltage.stop = False
        self.plot_widget_power.stop = False

    def stop(self):
        self.cbe_current.set_period(0)
        self.cbe_voltage.set_period(0)
        self.cbe_power.set_period(0)

        self.plot_widget_current.stop = True
        self.plot_widget_voltage.stop = True
        self.plot_widget_power.stop = True

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletVoltageCurrent.DEVICE_IDENTIFIER

    def cb_current(self, current):
        self.current_current.value = current / 1000.0

    def cb_voltage(self, voltage):
        self.current_voltage.value = voltage / 1000.0

    def cb_power(self, power):
        self.current_power.value = power / 1000.0

    def save_cal_clicked(self):
        gainmul = self.gainmul_spinbox.value()
        gaindiv = self.gaindiv_spinbox.value()
        self.vc.set_calibration(gainmul, gaindiv)

    def save_conf_clicked(self):
        avg = self.averaging_box.currentIndex()
        vol = self.voltage_box.currentIndex()
        cur = self.current_box.currentIndex()
        self.vc.set_configuration(avg, vol, cur)
