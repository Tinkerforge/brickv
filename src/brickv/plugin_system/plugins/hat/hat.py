# -*- coding: utf-8 -*-
"""
HAT Plugin
Copyright (C) 2018-2019 Olaf Lüke <olaf@tinkerforge.com>

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

from PyQt5.QtWidgets import QSpinBox, QSlider, QWidget, QAction
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize

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

        self.cbe_voltages = CallbackEmulator(self.hat.get_voltages,
                                             self.cb_voltages,
                                             self.increase_error_count)

        self.button_sleep.pressed.connect(self.button_sleep_pressed)
        self.bricklet_power_checkbox.stateChanged.connect(self.bricklet_power_changed)
        self.ports = [self.port_a, self.port_b, self.port_c, self.port_d, self.port_e, self.port_f, self.port_g, self.port_h]

    def bricklet_power_changed(self, state):
        self.hat.set_bricklet_power(state == Qt.Checked)

    def button_sleep_pressed(self):
        self.hat.set_sleep_mode(self.spinbox_sleep_delay.value(),
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
            info = infos.get_info(self.uid)

            for i in range(8):
                port = chr(ord('a') + i)

                try:
                    bricklet = info.connections_get(port)[0]
                    text = '{0} ({1})'.format(bricklet.name, bricklet.uid)
                    if text != self.ports[i].text():
                        self.ports[i].setText(text)
                        self.ports[i].mousePressEvent = self.get_port_label_clicked_lambda(bricklet.uid)
                except:
                    self.ports[i].setText('Not Connected')
        except:
            pass

    def get_bricklet_power_async(self, power):
        self.bricklet_power_checkbox.setChecked(power)

    def cb_voltages(self, voltages):
        self.label_voltage_usb.setText('{:.2f}V'.format(voltages.voltage_usb/1000.0))
        self.label_voltage_dc.setText('{:.2f}V'.format(voltages.voltage_dc/1000.0))

        self.update_bricklets()

    def start(self):
        async_call(self.hat.get_bricklet_power, None, self.get_bricklet_power_async, self.increase_error_count)
        self.cbe_voltages.set_period(250)

    def stop(self):
        self.cbe_voltages.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHAT.DEVICE_IDENTIFIER
