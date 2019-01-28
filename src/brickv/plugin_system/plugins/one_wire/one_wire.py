# -*- coding: utf-8 -*-
"""
One Wire Plugin
Copyright (C) 2018 Olaf Lüke <olaf@tinkerforge.com>

one_wire.py: 1-Wire Plugin Implementation

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

from PyQt5.QtWidgets import QTreeWidgetItem
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import pyqtSignal

from brickv.plugin_system.comcu_plugin_base import COMCUPluginBase
from brickv.bindings.bricklet_one_wire import BrickletOneWire
from brickv.plugin_system.plugins.one_wire.ui_one_wire import Ui_OneWire
from brickv.async_call import async_call
from brickv.hex_validator import HexValidator

import time

class OneWire(COMCUPluginBase, Ui_OneWire):
    def __init__(self, *args):
        COMCUPluginBase.__init__(self, BrickletOneWire, *args)

        self.setupUi(self)

        self.one_wire = self.device

        self.button_reset.clicked.connect(self.button_reset_clicked)
        self.button_search.clicked.connect(self.button_search_clicked)
        self.button_read_byte.clicked.connect(self.button_read_byte_clicked)
        self.button_write_byte.clicked.connect(self.button_write_byte_clicked)
        self.button_write_command.clicked.connect(self.button_write_command_clicked)

        self.start_time = time.time()

        self.ids = [0]

        self.write_data = 0
        self.write_command = 0
        self.write_command_id = 0

    def get_status_text(self, status):
        if status == 0:
            return 'OK'
        elif status == 1:
            return 'Busy'
        elif status == 2:
            return 'No Presence'
        elif status == 3:
            return 'Timeout'
        elif status == 4:
            return 'Error'
        else:
            return 'Unknown'

    def update_id_list(self):
        self.combo_box_write_command.clear()
        self.combo_box_write_command.addItem('Skip ID')
        for i in self.ids[1:]:
            self.combo_box_write_command.addItem('Match ID {0:X}'.format((i >> 8) & 0xFFFFFFFFFFFF))

    def add_to_list(self, command, value, status):
        self.tree_widget.insertTopLevelItem(0, QTreeWidgetItem([str(round(time.time()-self.start_time, 2)), command, value, self.get_status_text(status)]))

    def reset_bus_async(self, status):
        self.add_to_list('Reset Bus', '-', status)

    def button_reset_clicked(self):
        async_call(self.one_wire.reset_bus, None, self.reset_bus_async, self.increase_error_count)

    def search_bus_async(self, data):
        if not data.identifier:
            self.add_to_list('Search Bus', '-', data.status)
            return

        self.ids = [0]
        i = 0
        for identifier in data.identifier:
            self.ids.append(identifier)
            s = 'Family: {0:X}, ID: {1:X}, CRC: {2:X}'.format(identifier & 0xFF, (identifier >> 8) & 0xFFFFFFFFFFFF, identifier >> 56)
            if len(data.identifier) == 1:
                self.add_to_list('Search Bus', s, data.status)
            else:
                self.add_to_list('Search Bus ({0})'.format(i), s, data.status)
                i += 1

        self.update_id_list()

    def button_search_clicked(self):
        async_call(self.one_wire.search_bus, None, self.search_bus_async, self.increase_error_count)

    def read_byte_async(self, data):
        self.add_to_list('Read Byte', '{0:X}'.format(data.data), data.status)

    def button_read_byte_clicked(self):
        async_call(self.one_wire.read, None, self.read_byte_async, self.increase_error_count)

    def write_byte_async(self, status):
        self.add_to_list('Write Byte', '{0:X}'.format(self.write_data), status)

    def button_write_byte_clicked(self):
        self.write_data = self.spinbox_write_byte.value()
        async_call(self.one_wire.write, (self.write_data,), self.write_byte_async, self.increase_error_count)

    def write_command_async(self, status):
        self.add_to_list('Write Byte', '{0:X} to ID {1:X}'.format(self.write_command, self.write_command_id), status)

    def button_write_command_clicked(self):
        self.write_command_id = (self.ids[self.combo_box_write_command.currentIndex()] >> 8) & 0xFFFFFFFFFFFF
        self.write_command = self.spinbox_write_command.value()
        async_call(self.one_wire.write_command, (self.ids[self.combo_box_write_command.currentIndex()], self.write_command), self.write_command_async, self.increase_error_count)


    def start(self):
        pass

    def stop(self):
        pass

    def destroy(self):
        pass

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickletOneWire.DEVICE_IDENTIFIER
