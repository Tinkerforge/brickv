# -*- coding: utf-8 -*-
"""
brickv (Brick Viewer)
Copyright (C) 2012, 2014 Roland Dudko <roland.dudko@gmail.com>
Copyright (C) 2012, 2014 Marvin Lutz <marvin.lutz.mail@gmail.com>

device_dialog.py: Data logger device dialog

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

from PyQt4.QtGui import QDialog # , QMessageBox
from brickv.data_logger.loggable_devices import device_specs
from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import Utilities
from brickv.data_logger.ui_device_dialog import Ui_DeviceDialog
# from PyQt4 import QtGui, QtCore
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from PyQt4.QtCore import Qt
from brickv import infos

# noinspection PyTypeChecker
class DeviceDialog(QDialog, Ui_DeviceDialog):
    """
        Function and Event handling class for the Ui_DeviceDialog.
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent)

        self._logger_window = parent
        self._no_connected_device_string = "No Connected Devices found"
        self._list_separator_string = "----------------------------------------"
        self.Ui_Logger = None

        self.setupUi(self)
        self.signal_initialization()

    # noinspection PyUnresolvedReferences
    def signal_initialization(self):
        """
            Init of all important Signals and connections.
        """
        self.btn_add_device.clicked.connect(self.btn_add_device_clicked)
        self.btn_add_all_devices.clicked.connect(self.btn_add_all_devices_clicked)
        self.btn_cancel.clicked.connect(self._btn_cancel_clicked)

    def init_dialog(self, Ui_Logger):
        """
           Builds the Tree.
        """
        self.Ui_Logger = Ui_Logger

        self.btn_add_all_devices.setEnabled(len(infos.get_device_infos()) > 0)

        self._create_tree()

    def _btn_cancel_clicked(self):
        self.close()

    def btn_add_all_devices_clicked(self):
        for device_info in infos.get_device_infos():
            if device_info.name in device_specs:
                self._logger_window.add_device_to_tree(self.create_device_config('{0} [{1}]'.format(device_info.name, device_info.uid)))

    def btn_add_device_clicked(self):
        for item in self.list_widget.selectedItems():
            name = item.text()

            if name == self._no_connected_device_string or name == self._list_separator_string: # FIXME
                # ignore those
                continue

            self._logger_window.add_device_to_tree(self.create_device_config(name))

    def create_device_config(self, item_text):
        name, uid = Utilities.parse_device_name(item_text) # FIXME
        device_spec = device_specs[name]

        if uid == None: # FIXME
            uid = ''

        device = {
            'host': 'default',
            'name': name,
            'uid': uid,
            'values': {},
            'options': {}
        }

        for value_spec in device_spec['values']:
            device['values'][value_spec['name']] = {'interval': 0}

            if value_spec['subvalues'] != None:
                device['values'][value_spec['name']]['subvalues'] = {}

                for subvalue_name in value_spec['subvalues']:
                    device['values'][value_spec['name']]['subvalues'][subvalue_name] = True

        if device_spec['options'] != None:
            for option_spec in device_spec['options']:
                device['options'][option_spec['name']] = {'value': option_spec['default']}

        return device

    def _create_tree(self, connected_devices=0):
        """
            Create the tree in the corresponding Dialog Mode(Add/Remove).
        """
        list_blueprint = []

        # connected devices
        if connected_devices <= 0:
            connected_devices = infos.get_device_infos()

        if len(connected_devices) <= 0:
            list_blueprint.append(self._no_connected_device_string)
        else:
            for device_info in connected_devices:
                if device_info.name in device_specs:
                    list_blueprint.append(device_info.name + " [" + device_info.uid + "]")

        # self.combo_devices.insertSeparator(self.combo_devices.count() + 1)
        list_blueprint.append(self._list_separator_string)

        # list of all devices
        default_devices = []
        for device in device_specs:
            default_devices.append(device)
        default_devices.sort()
        for val in default_devices:
            list_blueprint.append(val)

        # add to list widget
        self.list_widget.clear()
        for dev in list_blueprint:
            self.list_widget.addItem(str(dev))
