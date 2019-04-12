# -*- coding: utf-8 -*-
"""
HAT Zero Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

hat_zero.py: HAT Zero Plugin Implementation

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

from PyQt5.QtCore import QTimer

from brickv.bindings.brick_hat_zero import BrickHATZero
from brickv.plugin_system.plugins.hat_zero.ui_hat_zero import Ui_HATZero
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.callback_emulator import CallbackEmulator
from brickv import infos
from brickv.utils import get_main_window

class HATZero(COMCUPluginBase, Ui_HATZero):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickHATZero, *args)

        self.setupUi(self)

        self.hat_zero = self.device

        self.cbe_voltage = CallbackEmulator(self.hat_zero.get_usb_voltage,
                                            None,
                                            self.cb_usb_voltage,
                                            self.increase_error_count)

        self.ports = [self.port_a, self.port_b, self.port_c, self.port_d]

        for port in self.ports:
            port.setProperty('_bricklet_uid', None)
            port.setEnabled(False)
            port.clicked.connect(self.port_clicked)

        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_bricklets)

    def cb_usb_voltage(self, voltage):
        self.label_usb_voltage.setText('{:.2f}V'.format(voltage/1000))

    def port_clicked(self):
        uid = self.sender().property('_bricklet_uid')

        if uid != None:
            get_main_window().show_plugin(uid)

    def update_bricklets(self):
        info = infos.get_info(self.uid)

        if info == None:
            return

        for i in range(4):
            port = chr(ord('a') + i)

            try:
                bricklet = info.connections_get(port)[0]
                text = '{0} ({1})'.format(bricklet.name, bricklet.uid)

                if text != self.ports[i].text():
                    self.ports[i].setText(text)
                    self.ports[i].setProperty('_bricklet_uid', bricklet.uid)
                    self.ports[i].setEnabled(True)
            except:
                self.ports[i].setText('Not Connected')
                self.ports[i].setProperty('_bricklet_uid', None)
                self.ports[i].setEnabled(False)

    def start(self):
        self.cbe_voltage.set_period(250)
        self.update_bricklets()
        self.update_timer.start(500)

    def stop(self):
        self.cbe_voltage.set_period(0)
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickHATZero.DEVICE_IDENTIFIER
