# -*- coding: utf-8 -*-
"""
XMC1400 Breakout Plugin
Copyright (C) 2017 Olaf Lüke <olaf@tinkerforge.com>

xmc1400_breakout.py: XMC1400 Breakout Plugin Implementation

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

import random

from PyQt4.QtGui import QTextCursor, QAction
from PyQt4.QtCore import pyqtSignal

from brickv.bindings.bricklet_xmc1400_breakout import BrickletXMC1400Breakout
from brickv.plugin_system.plugins.xmc1400_breakout.ui_xmc1400_breakout import Ui_XMC1400Breakout
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator
from brickv.callback_emulator import CallbackEmulator
from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.plugin_system.plugins.rs485.qhexedit import QHexeditWidget

MODE_RS485 = 0
MODE_MODBUS_SLAVE_RTU = 1
MODE_MODBUS_MASTER_RTU = 2

MODBUS_F_IDX_READ_COILS = 0
MODBUS_F_IDX_READ_HOLDING_REGISTERS = 1
MODBUS_F_IDX_WRITE_SINGLE_COIL = 2
MODBUS_F_IDX_WRITE_SINGLE_REGISTER = 3
MODBUS_F_IDX_WRITE_MULTIPLE_COILS = 4
MODBUS_F_IDX_WRITE_MULTIPLE_REGISTERS = 5
MODBUS_F_IDX_READ_DISCRETE_INPUTS = 6
MODBUS_F_IDX_READ_INPUT_REGISTERS = 7

MODBUS_EXCEPTION_REQUEST_TIMEOUT = -1

class XMC1400Breakout(COMCUPluginBase, Ui_XMC1400Breakout):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletXMC1400Breakout, *args)

        self.setupUi(self)

        self.xmc1400_breakout = self.device

    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    def get_url_part(self):
        return 'xmc1400_breakout'

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletXMC1400Breakout.DEVICE_IDENTIFIER
