# -*- coding: utf-8 -*-
"""
Isolator Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

isolator.py: Isolator Plugin Implementation

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

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QCheckBox, QLabel

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.isolator.ui_isolator import Ui_Isolator 
from brickv.bindings.bricklet_isolator import BrickletIsolator
from brickv.plot_widget import PlotWidget, CurveValueWrapper
from brickv.async_call import async_call
from brickv.callback_emulator import CallbackEmulator

from brickv import infos
from brickv.utils import get_main_window

class Isolator(COMCUPluginBase, Ui_Isolator):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletIsolator, *args)
        self.setupUi(self)

        self.isolator = self.device

        self.cbe_statistics = CallbackEmulator(self.isolator.get_statistics,
                                               self.cb_get_statistics,
                                               self.increase_error_count)

        self.last_connected = None

    def cb_get_statistics(self, statistics):
        self.label_messages_from_brick.setText(str(statistics.messages_from_brick))
        self.label_messages_from_bricklet.setText(str(statistics.messages_from_bricklet))

        try:
            name = infos.get_info(statistics.connected_bricklet_uid).plugin.device_class.DEVICE_DISPLAY_NAME
        except:
            name = None
        if statistics.connected_bricklet_uid != '' and name != None:
            self.label_isolated_bricklet.setText('<b>{0}</b> with UID "{1}"'.format(name, statistics.connected_bricklet_uid))
            self.button_bricklet.setText('Open {0}'.format(name))
            if self.last_connected != statistics.connected_bricklet_uid:
                self.last_connected = statistics.connected_bricklet_uid
                try:
                    self.button_bricklet.clicked.disconnect()
                except:
                    pass
                self.button_bricklet.clicked.connect(lambda: get_main_window().show_plugin(statistics.connected_bricklet_uid))
            self.button_bricklet.setEnabled(True)
        else:
            self.label_isolated_bricklet.setText('Unknown Bricklet (Did you connect a Bricklet?)')
            self.button_bricklet.setText('Open Bricklet')
            self.button_bricklet.setEnabled(False)
                                
    def start(self):
        self.cbe_statistics.set_period(200)

    def stop(self):
        self.cbe_statistics.set_period(0)

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletIsolator.DEVICE_IDENTIFIER
