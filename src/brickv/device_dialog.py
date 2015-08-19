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

# -*- coding: utf-8 -*-
from PyQt4.QtGui import QDialog # , QMessageBox
from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import Utilities
from brickv.ui_device_dialog import Ui_DeviceDialog
# from PyQt4 import QtGui, QtCore
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from PyQt4.QtCore import Qt
from brickv import infos

from brickv.data_logger.loggable_devices import Identifier


# noinspection PyTypeChecker
class LoggerDeviceDialog(QDialog, Ui_DeviceDialog):
    """
        Function and Event handling class for the Ui_DeviceDialog.
    """

    def __init__(self, parent):
        QDialog.__init__(self, parent)
        self.setWindowFlags(Qt.Window | Qt.WindowCloseButtonHint)

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
        self.btn_add_device.clicked.connect(self._btn_add_device_clicked)
        self.btn_add_all_devices.clicked.connect(self._btn_add_all_devices_clicked)
        self.btn_cancel.clicked.connect(self._btn_cancel_clicked)

    def init_dialog(self, Ui_Logger):
        """
           Builds the Tree.
        """
        self.Ui_Logger = Ui_Logger

        connected_devices = infos.get_device_infos()
        if len(connected_devices) <= 0:
            self.btn_add_all_devices.setEnabled(False)
        else:
            self.btn_add_all_devices.setEnabled(True)

        self._create_tree()

    def _btn_cancel_clicked(self):
        self.close()

    def _btn_add_all_devices_clicked(self):
        cur_dev = GuiConfigHandler.get_simple_blueprint(self.Ui_Logger)
        connected_devices = infos.get_device_infos()
        if len(connected_devices) <= 0:
            return
        con_dev = []
        for device_info in connected_devices:
            if device_info.name in Identifier.DEVICE_DEFINITIONS:
                tmp = {}
                tmp[device_info.name] = device_info.uid
                con_dev.append(tmp)

        for dev in con_dev:
            for key in dev.keys():
                if not self.__is_device_in_list(key, dev[key], cur_dev):
                    blueprint = GuiConfigHandler.get_device_blueprint(key)
                    if blueprint is None:
                        return
                    blueprint[Identifier.DD_UID] = dev[key]
                    self._logger_window.add_item_to_tree(blueprint)

    def __is_device_in_list(self, device_name, uid, list_to_check):
        for dev in list_to_check:
            for key in dev.keys():
                if device_name == key and uid == dev[key]:
                    # device matches -> return True
                    return True
        return False

    def _btn_add_device_clicked(self):
        """
            Add the selected device from the list/DataLogger-Config.
        """
        items = self.list_widget.selectedItems()
        cur_dev = GuiConfigHandler.get_simple_blueprint(self.Ui_Logger)
        for item in items:
            name = item.text()
            if name == self._no_connected_device_string or name == self._list_separator_string:
                # ignore those
                continue

            dev_name, uid = Utilities.parse_device_name(name)
            dev = GuiConfigHandler.get_device_blueprint(dev_name)
            if dev is None:
                EventLogger.debug("DeviceDialog._btn_add_device_clicked: Blueprint(" + str(dev_name) + ") was None!")
                continue

            if uid is not None:
                if self.__is_device_in_list(dev_name, uid, cur_dev):
                    continue
                # else
                dev[Identifier.DD_UID] = uid

            else:
                dev[Identifier.DD_UID] = Identifier.DD_UID_DEFAULT

            self._logger_window.add_item_to_tree(dev)

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
                if device_info.name in Identifier.DEVICE_DEFINITIONS:
                    list_blueprint.append(device_info.name + " [" + device_info.uid + "]")

        # self.combo_devices.insertSeparator(self.combo_devices.count() + 1)
        list_blueprint.append(self._list_separator_string)

        # list of all devices
        default_devices = []
        for device in Identifier.DEVICE_DEFINITIONS:
            default_devices.append(device)
        default_devices.sort()
        for val in default_devices:
            list_blueprint.append(val)

        # add to list widget
        self.list_widget.clear()
        for dev in list_blueprint:
            self.list_widget.addItem(str(dev))
