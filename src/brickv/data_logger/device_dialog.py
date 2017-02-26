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

#### skip here for brick-logger ####

from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QDialog, QTreeWidgetItem

from brickv.data_logger.loggable_devices import device_specs
from brickv.data_logger.event_logger import EventLogger
from brickv.data_logger.utils import Utilities
from brickv.data_logger.ui_device_dialog import Ui_DeviceDialog
from brickv.data_logger.gui_config_handler import GuiConfigHandler
from brickv.bindings.ip_connection import IPConnection
from brickv.bindings import device_factory
from brickv.utils import get_modeless_dialog_flags

# noinspection PyTypeChecker
class DeviceDialog(QDialog, Ui_DeviceDialog):
    """
        Function and Event handling class for the Ui_DeviceDialog.
    """
    qtcb_enumerate = pyqtSignal(str, str, 'char', type((0,)), type((0,)), int, int)
    qtcb_connected = pyqtSignal(int)

    def __init__(self, parent):
        QDialog.__init__(self, parent, get_modeless_dialog_flags())

        self._logger_window = parent

        self.qtcb_enumerate.connect(self.cb_enumerate)
        self.qtcb_connected.connect(self.cb_connected)

        self.host = None
        self.port = None
        self.secret = None

        self.ipcon = IPConnection()
        self.ipcon.register_callback(IPConnection.CALLBACK_CONNECTED,
                                     self.qtcb_connected.emit)
        self.ipcon.register_callback(IPConnection.CALLBACK_ENUMERATE,
                                     self.qtcb_enumerate.emit)

        self.setupUi(self)

        self.btn_add_device.clicked.connect(self.btn_add_device_clicked)
        self.btn_refresh.clicked.connect(self.btn_refresh_clicked)
        self.btn_close.clicked.connect(self.btn_close_clicked)
        self.tree_widget.itemActivated.connect(self.add_item)

        self.connected_uids = []
        self.available_item = QTreeWidgetItem(['No devices available'])
        self.supported_item = QTreeWidgetItem(['Supported devices'])

        self.tree_widget.addTopLevelItem(self.available_item)
        self.tree_widget.addTopLevelItem(self.supported_item)

        for device_name in device_specs:
            self.supported_item.addChild(QTreeWidgetItem([device_name]))

        self.supported_item.sortChildren(0, Qt.AscendingOrder)
        self.supported_item.setExpanded(True)

    def cb_connected(self, connect_reason):
        self.tree_widget.clearSelection()
        self.available_item.takeChildren()
        self.available_item.setExpanded(True)
        self.available_item.setText(0, 'No devices available at {0}:{1}'.format(self.host, self.port))

        self.connected_uids = []

        if self.secret != None:
            self.ipcon.set_auto_reconnect(False) # don't auto-reconnect on authentication error

            try:
                self.ipcon.authenticate(self.secret)
            except:
                try:
                    self.ipcon.disconnect()
                except:
                    pass

                if connect_reason == IPConnection.CONNECT_REASON_AUTO_RECONNECT:
                    extra = ' after auto-reconnect'
                else:
                    extra = ''

                self.available_item.setText(0, 'Could not authenticate' + extra)
                return

            self.ipcon.set_auto_reconnect(True)

        try:
            self.ipcon.enumerate()
        except:
            pass

    def cb_enumerate(self, uid, connected_uid, position,
                     hardware_version, firmware_version,
                     device_identifier, enumeration_type):
        if enumeration_type in [IPConnection.ENUMERATION_TYPE_AVAILABLE,
                                IPConnection.ENUMERATION_TYPE_CONNECTED]:
            if uid not in self.connected_uids:
                try:
                    display_name = device_factory.get_device_display_name(device_identifier)
                except KeyError:
                    return # unknown device identifier

                if display_name in device_specs:
                    self.connected_uids.append(uid)
                    self.available_item.addChild(QTreeWidgetItem(['{0} [{1}]'.format(display_name, uid)]))
                    self.available_item.setText(0, 'Devices available at {0}:{1}'.format(self.host, self.port))
                    self.available_item.sortChildren(0, Qt.AscendingOrder)
        else:
            if uid in self.connected_uids:
                self.connected_uids.remove(uid)

            for i in range(self.available_item.childCount()):
                child = self.available_item.child(i)

                if '[{0}]'.format(uid) in child.text(0):
                    self.available_item.takeChild(i)
                    break

            if self.available_item.childCount() == 0:
                self.available_item.setText(0, 'No devices available at {0}:{1}'.format(self.host, self.port))

    def btn_add_device_clicked(self):
        for item in self.tree_widget.selectedItems():
            if item == self.available_item or item == self.supported_item:
                continue

            self._logger_window.add_device_to_tree(self.create_device_config(item.text(0)))

    def btn_refresh_clicked(self):
        try:
            self.ipcon.disconnect()
        except:
            pass

        self.tree_widget.clearSelection()
        self.available_item.takeChildren()
        self.available_item.setExpanded(True)

        self.connected_uids = []
        self.host = self._logger_window.combo_host.currentText()
        self.port = self._logger_window.spin_port.value()

        if self._logger_window.check_authentication.isChecked():
            try:
                self.secret = self._logger_window.edit_secret.text().encode('ascii')
            except:
                self.secret = None
        else:
            self.secret = None

        try:
            self.ipcon.connect(self.host, self.port)
            self.available_item.setText(0, 'No devices available at {0}:{1}'.format(self.host, self.port))
        except:
            self.available_item.setText(0, 'Could not connect to {0}:{1}'.format(self.host, self.port))

    def btn_close_clicked(self):
        self.close()

    def add_item(self, item):
        if item == self.available_item or item == self.supported_item:
            return

        self._logger_window.add_device_to_tree(self.create_device_config(item.text(0)))

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
