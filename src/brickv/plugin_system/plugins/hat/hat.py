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

from brickv import infos
from brickv.utils import get_main_window

from datetime import datetime

class HAT(COMCUPluginBase, Ui_HAT):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletHAT, *args)

        self.setupUi(self)

        self.hat = self.device
              
        self.cbe_battery_statistics = CallbackEmulator(self.hat.get_battery_statistics,
                                                       self.cb_battery_statistics,
                                                       self.increase_error_count) 

        self.cbe_time = CallbackEmulator(self.hat.get_time,
                                         self.cb_time,
                                         self.increase_error_count)

        self.button_sleep.pressed.connect(self.button_sleep_pressed)
        self.button_time_manual.pressed.connect(self.button_time_manual_pressed)
        self.button_time_system.pressed.connect(self.button_time_system_pressed)

        self.ports = [self.port_a, self.port_b, self.port_c, self.port_d, self.port_e, self.port_f, self.port_g, self.port_h]
        self.time_widgets = [self.spin_year, self.spin_month, self.spin_day, self.spin_hour, self.spin_minute, self.spin_second, self.combo_weekday]

        self.manual_time_set_active = False
        self.update_time_widget_enabled()

    def update_time_widget_enabled(self):
        for widget in self.time_widgets:
            widget.setEnabled(self.manual_time_set_active)

        self.button_time_system.setEnabled(not self.manual_time_set_active)
    
    def button_time_manual_pressed(self):
        if self.manual_time_set_active:
            year = self.spin_year.value()
            month = self.spin_month.value() - 1
            day = self.spin_day.value()
            hour = self.spin_hour.value()
            minute = self.spin_minute.value()
            second = self.spin_second.value()
            weekday = self.combo_weekday.currentIndex() + 1
            
            self.hat.set_time(year, month, day, hour, minute, second, weekday)
            self.button_time_manual.setText('Set Time Manually')
        else:
            self.button_time_manual.setText('Use Time')

        self.manual_time_set_active = not self.manual_time_set_active
        self.update_time_widget_enabled()

    def button_time_system_pressed(self):
        now = datetime.now()

        year = now.year
        month = now.month - 1
        day = now.day
        hour = now.hour
        minute = now.minute
        second = now.second
        weekday = now.weekday() + 1

        self.hat.set_time(year, month, day, hour, minute, second, weekday)

    def button_sleep_pressed(self):
        self.hat.set_power_off(self.spinbox_sleep_delay.value(), 
                               self.spinbox_sleep_duration.value(), 
                               self.checkbox_rpi_off.isChecked(), 
                               self.checkbox_bricklets_off.isChecked(),
                               self.checkbox_sleep_indicator.isChecked())

    def port_label_clicked(self, event, uid):
        get_main_window().show_plugin(uid)

    def get_port_label_clicked_lambda(self, uid):
        return lambda x: self.port_label_clicked(x, uid)

    def update_bricklets(self):
        try:
            bricklets = infos.get_info(self.uid).connections
            for i in range(8):
                port = chr(ord('a') + i)
                try:
                    bricklet = bricklets[port]
                    text ='{0} ({1})'.format(bricklet.name, bricklet.uid) 
                    if text != self.ports[i].text():
                        self.ports[i].setText(text)
                        self.ports[i].mousePressEvent = self.get_port_label_clicked_lambda(bricklet.uid)
                except:
                    self.ports[i].setText('Not Connected')
        except:
            pass

    def cb_time(self, time):
        if not self.manual_time_set_active:
            self.spin_year.setValue(time.year)
            self.spin_month.setValue(time.month+1)
            self.spin_day.setValue(time.day)
            self.spin_hour.setValue(time.hour)
            self.spin_minute.setValue(time.minute)
            self.spin_second.setValue(time.second)
            self.combo_weekday.setCurrentIndex(time.weekday-1)

        # Use the callback to also update list of Bricklets.
        self.update_bricklets()

    def cb_battery_statistics(self, stats):
        if stats.battery_connected:
            self.label_battery_connected.setText('Yes')
        else:
            self.label_battery_connected.setText('No')


        self.label_capacity_full.setText('{0}mAh'.format(stats.capacity_full))
        self.label_capacity_nominal.setText('{0}mAh'.format(stats.capacity_nominal))
        self.label_capacity_remaining.setText('{0}mAh'.format(stats.capacity_remaining))
        self.label_percentage_charge.setText(u'{:.2f}%'.format(stats.percentage_charge/100.0))
        self.label_voltage_battery.setText('{:.2f}V'.format(stats.voltage_battery/1000.0))
        self.label_voltage_usb.setText('{:.2f}V'.format(stats.voltage_usb/1000.0))
        self.label_voltage_dc.setText('{:.2f}V'.format(stats.voltage_dc/1000.0))
        self.label_current_flow.setText('{:.2f}A'.format(stats.current_flow/1000.0))
        self.label_temperature_battery.setText(u'{:.2f}°C'.format(stats.temperature_battery/100.0))



    def start(self):
        self.cbe_battery_statistics.set_period(250)
        self.cbe_time.set_period(1000)

    def stop(self):
        self.cbe_battery_statistics.set_period(0)
        self.cbe_time.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHAT.DEVICE_IDENTIFIER
