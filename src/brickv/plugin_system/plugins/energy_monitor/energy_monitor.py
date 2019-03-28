# -*- coding: utf-8 -*-
"""
Energy Monitor Plugin
Copyright (C) 2019 Olaf Lüke <olaf@tinkerforge.com>

energy_monitor.py: Energy Monitor Plugin Implementation

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

from PyQt5.QtWidgets import QVBoxLayout, QWidget, QSpinBox, QSlider, QSizePolicy, QAction

from PyQt5.QtGui import QLinearGradient, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize

from brickv.bindings.bricklet_energy_monitor import BrickletEnergyMonitor
from brickv.plugin_system.plugins.energy_monitor.ui_energy_monitor import Ui_EnergyMonitor
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plot_widget import PlotWidget

import math

ENERGY_MONITOR_MS_PER_TICK = 0.07185

class EnergyMonitor(COMCUPluginBase, Ui_EnergyMonitor):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletEnergyMonitor, *args)

        self.setupUi(self)

        self.energy_monitor = self.device
        self.cbe_get_waveform = CallbackEmulator(self.energy_monitor.get_waveform,
                                                 self.cb_waveform,
                                                 self.increase_error_count)
        self.cbe_get_energy_data = CallbackEmulator(self.energy_monitor.get_energy_data,
                                                    self.cb_energy_data,
                                                    self.increase_error_count)

        plots_waveform_v = [('Waveform V', Qt.red, None, None)]
        self.plot_widget_waveform_v = PlotWidget('Voltage [V]', plots_waveform_v, clear_button=None, x_diff=768*ENERGY_MONITOR_MS_PER_TICK, x_scale_title_text='Time [ms]', key=None, x_scale_visible=False)
        self.plot_widget_waveform_v.set_x_scale(10, 1)

        plots_waveform_a = [('Waveform A', Qt.red, None, None)]
        self.plot_widget_waveform_a = PlotWidget('Current [A]', plots_waveform_a, clear_button=None, x_diff=768*ENERGY_MONITOR_MS_PER_TICK, x_scale_title_text='Time [ms]', key=None)
        self.plot_widget_waveform_a.set_x_scale(10, 1)

        self.layout_graph.insertWidget(0, self.plot_widget_waveform_v)
        self.layout_graph.addWidget(self.plot_widget_waveform_a)
        self.x_data = [x * ENERGY_MONITOR_MS_PER_TICK for x in list(range(768))]

    def cb_waveform(self, waveform):
        y_data_v = [x*0.1 for x in waveform[::2]]
        y_data_a = [x*0.01 for x in waveform[1::2]]
        self.plot_widget_waveform_v.set_data(0, self.x_data, y_data_v)
        self.plot_widget_waveform_a.set_data(0, self.x_data, y_data_a)
    
    def cb_energy_data(self, data):
        self.label_voltage.setText('{0:.2f}'.format(data.voltage/100))
        self.label_current.setText('{0:.2f}'.format(data.current/100))
        self.label_energy.setText('{0:.2f}'.format(data.energy/100))
        self.label_real_power.setText('{0:.2f}'.format(data.real_power/100))
        self.label_apparent_power.setText('{0:.2f}'.format(data.apparent_power/100))
        self.label_reactive_power.setText('{0:.2f}'.format(data.reactive_power/100))
        self.label_power_factor.setText('{0:.2f}'.format((data.power_factor//10)/100))
        self.label_frequency.setText('{0:.2f}'.format(data.frequency/100))

    def start(self):
        async_call(self.energy_monitor.get_waveform, None, self.cb_waveform, self.increase_error_count)
        self.cbe_get_waveform.set_period(500)
        self.cbe_get_energy_data.set_period(200)

    def stop(self):
        self.cbe_get_waveform.set_period(0)
        self.cbe_get_energy_data.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletEnergyMonitor.DEVICE_IDENTIFIER
