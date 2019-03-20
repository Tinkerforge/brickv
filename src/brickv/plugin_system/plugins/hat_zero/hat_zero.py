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

from PyQt5.QtWidgets import QSpinBox, QSlider, QWidget, QAction
from PyQt5.QtGui import QImage, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QSize, QTimer

from brickv.bindings.bricklet_hat_zero import BrickletHATZero
from brickv.plugin_system.plugins.hat_zero.ui_hat_zero import Ui_HATZero
from brickv.async_call import async_call
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.callback_emulator import CallbackEmulator

from brickv import infos
from brickv.utils import get_main_window

from datetime import datetime

class HATZero(COMCUPluginBase, Ui_HATZero):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletHATZero, *args)

        self.setupUi(self)

        self.hat_zero = self.device
        self.ports = [self.port_a, self.port_b, self.port_c, self.port_d]
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_bricklets)

    def port_label_clicked(self, event, uid):
        get_main_window().show_plugin(uid)

    def get_port_label_clicked_lambda(self, uid):
        return lambda x: self.port_label_clicked(x, uid)

    def update_bricklets(self):
        try:
            bricklets = infos.get_info(self.uid).connections

            for i in range(4):
                port = chr(ord('a') + i)

                try:
                    bricklet = bricklets[port]
                    text = '{0} ({1})'.format(bricklet.name, bricklet.uid)
                    if text != self.ports[i].text():
                        self.ports[i].setText(text)
                        self.ports[i].mousePressEvent = self.get_port_label_clicked_lambda(bricklet.uid)
                except:
                    self.ports[i].setText('Not Connected')
        except:
            pass

    def start(self):
        self.update_timer.start(500)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletHATZero.DEVICE_IDENTIFIER
