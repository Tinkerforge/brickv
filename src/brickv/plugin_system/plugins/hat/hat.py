# -*- coding: utf-8 -*-
"""
HAT Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

hat.py: HAT Plugin Implementation

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

from PyQt4.QtGui import QSpinBox, QSlider, QWidget, QImage, QPainter, QPen, QAction
from PyQt4.QtCore import pyqtSignal, Qt, QPoint, QSize

from brickv.bindings.bricklet_hat import BrickletHAT
from brickv.plugin_system.plugins.hat.ui_hat import Ui_HAT
from brickv.async_call import async_call
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.callback_emulator import CallbackEmulator

class HAT(COMCUPluginBase, Ui_HAT):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletHAT, *args)

        self.setupUi(self)

        self.hat = self.device
              
        self.cbe_battery_statistics = CallbackEmulator(self.hat.get_battery_statistics,
                                                       self.cb_battery_statistics,
                                                       self.increase_error_count) 
        self.button_sleep.pressed.connect(self.button_sleep_pressed)
        
    def button_sleep_pressed(self):
        self.hat.set_power_off(self.spinbox_sleep_delay.value(), 
                               self.spinbox_sleep_duration.value(), 
                               self.checkbox_rpi_off.isChecked(), 
                               self.checkbox_bricklets_off.isChecked(),
                               self.checkbox_sleep_indicator.isChecked())

    def cb_battery_statistics(self, stats):
        if stats.battery_connected:
            self.label_battery_connected.setText('Yes')
        else:
            self.label_battery_connected.setText('No')


        self.label_capacity_full.setText('{0}mAh'.format(stats.capacity_full))
        self.label_capacity_nominal.setText('{0}mAh'.format(stats.capacity_nominal))
        self.label_capacity_remaining.setText('{0}mAh'.format(stats.capacity_remaining))
        self.label_percentage_charge.setText(u'{:.2f}%'.format(stats.percentage_charge/100.0))
        self.label_time_to_empty.setText('{0}min'.format(int(stats.time_to_empty/60)))
        self.label_time_to_full.setText('{0}min'.format(int(stats.time_to_full/60)))
        self.label_voltage_battery.setText('{:.2f}V'.format(stats.voltage_battery/1000.0))
        self.label_voltage_usb.setText('{:.2f}V'.format(stats.voltage_usb/1000.0))
        self.label_voltage_dc.setText('{:.2f}V'.format(stats.voltage_dc/1000.0))
        self.label_current_flow.setText('{:.2f}A'.format(stats.current_flow/1000.0))
        self.label_temperature_battery.setText(u'{:.2f}°C'.format(stats.temperature_battery/100.0))

    def start(self):
        self.cbe_battery_statistics.set_period(250)

    def stop(self):
        self.cbe_battery_statistics.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHAT.DEVICE_IDENTIFIER
