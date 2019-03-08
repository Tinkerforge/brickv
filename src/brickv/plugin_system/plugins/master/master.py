# -*- coding: utf-8 -*-
"""
Master Plugin
Copyright (C) 2010-2012 Olaf Lüke <olaf@tinkerforge.com>
Copyright (C) 2014-2016 Matthias Bolte <matthias@tinkerforge.com>

master.py: Master Plugin implementation

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
from PyQt5.QtWidgets import QAction, QTabBar
from PyQt5.QtGui import QIcon

from brickv.plugin_system.plugin_base import PluginBase
from brickv.plugin_system.plugins.master.ui_master import Ui_Master
from brickv.plugin_system.plugins.master.extension_type import ExtensionType
from brickv.plugin_system.plugins.master.chibi import Chibi
from brickv.plugin_system.plugins.master.rs485 import RS485
from brickv.plugin_system.plugins.master.wifi import Wifi
from brickv.plugin_system.plugins.master.ethernet import Ethernet
from brickv.plugin_system.plugins.master.wifi2 import Wifi2
from brickv.bindings.brick_master import BrickMaster
from brickv.async_call import async_call
from brickv import infos
from brickv.utils import get_main_window, format_current
from brickv.tab_window import IconButton
from brickv.load_pixmap import load_pixmap

class Master(PluginBase, Ui_Master):
    def __init__(self, *args):
        PluginBase.__init__(self, BrickMaster, *args)

        self.setupUi(self)

        self.master = self.device

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)

        self.wifi2_get_firmware_version_timer = QTimer()
        self.wifi2_get_firmware_version_timer.timeout.connect(self.wifi2_get_firmware_version)

        self.extension_type = None

        self.extensions = []
        self.num_extensions = 0
        self.wifi2_ext = None
        self.wifi2_firmware_version = None
        self.wifi_update_button = IconButton(QIcon(load_pixmap('update-icon-normal.png')), QIcon(load_pixmap('update-icon-hover.png')), self.tab_widget)
        self.wifi_update_button.setToolTip('Extension update available')
        self.wifi_update_button.clicked.connect(lambda: get_main_window().show_extension_update(self.device_info.uid))
        self.wifi_update_button.hide()

        self.wifi_update_available = False
        self.wifi_tab_idx = None

        self.extension_label.setText("None Present")
        self.tab_widget.removeTab(0)
        self.tab_widget.hide()

        if self.firmware_version >= (1, 1, 0):
            self.check_extensions = True
            self.extension_type_button.clicked.connect(self.extension_clicked)
        else:
            self.check_extensions = False
            self.extension_type_button.setEnabled(False)

        if self.firmware_version >= (2, 3, 2):
            self.status_led_action = QAction('Status LED', self)
            self.status_led_action.setCheckable(True)
            self.status_led_action.toggled.connect(lambda checked: self.master.enable_status_led() if checked else self.master.disable_status_led())
            self.set_configs([(0, None, [self.status_led_action])])
        else:
            self.status_led_action = None

        if self.firmware_version >= (1, 2, 1):
            reset = QAction('Reset', self)
            reset.triggered.connect(lambda: self.master.reset())
            self.set_actions([(0, None, [reset])])

        self.extension_type_preset = [None,  # None
                                      False, # Chibi
                                      False, # RS485
                                      False, # WIFI
                                      False, # Ethernet
                                      False] # WIFI 2.0

        self.update_extensions_in_device_info()

    # overrides PluginBase.device_infos_changed
    def device_infos_changed(self, uid):
        if uid != self.device_info.uid:
            return

        if self.extension_type_preset[self.master.EXTENSION_TYPE_WIFI2]:
            wifi_info = next(ext for ext in self.device_info.extensions.values() if ext.extension_type == self.master.EXTENSION_TYPE_WIFI2)
            wifi_update_avail = wifi_info.firmware_version_installed != (0,0,0) and wifi_info.firmware_version_installed < wifi_info.firmware_version_latest
        else:
            wifi_update_avail = False

        brick_update_avail = self.device_info.firmware_version_installed < self.device_info.firmware_version_latest

        tab_idx = get_main_window().tab_widget.indexOf(self.device_info.tab_window)

        if not brick_update_avail and not wifi_update_avail:
            if self.device_info.tab_window is not None:
                self.device_info.tab_window.button_update.hide()
            get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, None)

            if self.wifi_tab_idx is not None:
                self.tab_widget.tabBar().setTabButton(self.wifi_tab_idx, QTabBar.LeftSide, None)
                if self.wifi_update_button is not None:
                    self.wifi_update_button.hide()
            return

        self.update_tab_button = IconButton(QIcon(load_pixmap('update-icon-normal.png')), QIcon(load_pixmap('update-icon-hover.png')))

        if brick_update_avail:
            if self.device_info.tab_window is not None:
                self.device_info.tab_window.button_update.show()
            self.update_tab_button.setToolTip('Master Brick update available')
            self.update_tab_button.clicked.connect(lambda: get_main_window().show_brick_update(self.device_info.url_part))

            if self.wifi_tab_idx is not None:
                self.tab_widget.tabBar().setTabButton(self.wifi_tab_idx, QTabBar.LeftSide, None)
                if self.wifi_update_button is not None:
                    self.wifi_update_button.hide()

        # Intentionally override possible Master Brick update notification: The Extension update is easier for users
        # so they are more likely to update at least the Extension. Also when the Extension is updated, device_infos_changed
        # will be called again, then notifying the user of the Master Brick update.
        if wifi_update_avail:
            self.update_tab_button.setToolTip('WIFI Extension update available')
            self.update_tab_button.clicked.connect(lambda: get_main_window().show_extension_update(self.device_info.uid))

            if self.wifi_tab_idx is not None:
                self.tab_widget.tabBar().setTabButton(self.wifi_tab_idx, QTabBar.LeftSide, self.wifi_update_button)
                self.wifi_update_button.show()


        get_main_window().tab_widget.tabBar().setTabButton(tab_idx, QTabBar.RightSide, self.update_tab_button)

    def update_extensions_in_device_info(self):
        def is_present_async(present, extension_type, name):
            self.extension_type_preset[extension_type] = present

            if present:
                if self.device_info.extensions['ext0'] == None:
                    ext = 'ext0'
                elif self.device_info.extensions['ext1'] == None:
                    ext = 'ext1'
                else:
                    return # This should never be the case

                self.device_info.extensions[ext] = infos.ExtensionInfo()
                self.device_info.extensions[ext].name = name
                self.device_info.extensions[ext].extension_type = extension_type
                self.device_info.extensions[ext].position = ext
                self.device_info.extensions[ext].master_info = self.device_info

                if extension_type == self.master.EXTENSION_TYPE_WIFI2:
                    self.device_info.extensions[ext].url_part = 'wifi_v2'
                    # When WIFI2 extension firmware version is being requested the
                    # extension might still not be done with booting and thus the
                    # message won't be received by the extension. So we delay sending
                    # the request which gives enough time to the extension to finish
                    # booting. Note that this delay is only induced when there is a
                    # WIFI2 extension present.
                    self.wifi2_ext = ext
                    self.label_no_extension.setText('Waiting for WIFI Extension 2.0 firmware version...')
                    self.wifi2_get_firmware_version_timer.start(2000)

                infos.update_info(self.uid)

        def get_connection_type_async(connection_type):
            self.device_info.connection_type = connection_type
            infos.update_info(self.uid)

        if self.firmware_version >= (1, 1, 0):
            async_call(self.master.is_chibi_present, None, lambda p: is_present_async(p, self.master.EXTENSION_TYPE_CHIBI, 'Chibi Extension'), self.increase_error_count)

        if self.firmware_version >= (1, 2, 0):
            async_call(self.master.is_rs485_present, None, lambda p: is_present_async(p, self.master.EXTENSION_TYPE_RS485, 'RS485 Extension'), self.increase_error_count)

        if self.firmware_version >= (1, 3, 0):
            async_call(self.master.is_wifi_present, None, lambda p: is_present_async(p, self.master.EXTENSION_TYPE_WIFI, 'WIFI Extension'), self.increase_error_count)

        if self.firmware_version >= (2, 1, 0):
            async_call(self.master.is_ethernet_present, None, lambda p: is_present_async(p, self.master.EXTENSION_TYPE_ETHERNET, 'Ethernet Extension'), self.increase_error_count)

        if self.firmware_version >= (2, 4, 0):
            async_call(self.master.is_wifi2_present, None, lambda p: is_present_async(p, self.master.EXTENSION_TYPE_WIFI2, 'WIFI Extension 2.0'), self.increase_error_count)
            async_call(self.master.get_connection_type, None, get_connection_type_async, self.increase_error_count)

        async_call(lambda: None, None, lambda: get_main_window().update_tree_view(), None)

    def get_wifi2_firmware_version_async(self, version):
        self.wifi2_firmware_version = version
        self.device_info.extensions[self.wifi2_ext].firmware_version_installed = version
        infos.update_info(self.uid)
        get_main_window().update_tree_view() # FIXME: this is kind of a hack
        self.wifi2_present(True)

    def wifi2_get_firmware_version(self):
        if self.wifi2_firmware_version != None:
            return

        self.wifi2_get_firmware_version_timer.stop()
        async_call(self.master.get_wifi2_firmware_version, None, self.get_wifi2_firmware_version_async, self.increase_error_count)


    def wifi2_present(self, present):
        if present and self.wifi2_firmware_version != None and not self.check_extensions:
            wifi2 = Wifi2(self.wifi2_firmware_version, self)
            wifi2.start()
            self.extensions.append(wifi2)
            self.wifi_tab_idx = self.tab_widget.addTab(wifi2, 'WIFI 2.0')
            self.device_infos_changed(self.device_info.uid) # Trigger device_infos_changed to show potential wifi updates.
            self.tab_widget.show()
            self.num_extensions += 1
            self.extension_label.setText(str(self.num_extensions) + " Present")
            self.label_no_extension.hide()

    def ethernet_present(self, present):
        if present:
            ethernet = Ethernet(self)
            ethernet.start()
            self.extensions.append(ethernet)
            self.tab_widget.addTab(ethernet, 'Ethernet')
            self.tab_widget.show()
            self.num_extensions += 1
            self.extension_label.setText(str(self.num_extensions) + " Present")
            self.label_no_extension.hide()

    def wifi_present(self, present):
        if present:
            wifi = Wifi(self)
            wifi.start()
            self.extensions.append(wifi)
            self.tab_widget.addTab(wifi, 'WIFI')
            self.tab_widget.show()
            self.num_extensions += 1
            self.extension_label.setText(str(self.num_extensions) + " Present")
            self.label_no_extension.hide()

    def rs485_present(self, present):
        if present:
            rs485 = RS485(self)
            rs485.start()
            self.extensions.append(rs485)
            self.tab_widget.addTab(rs485, 'RS485')
            self.tab_widget.show()
            self.num_extensions += 1
            self.extension_label.setText(str(self.num_extensions) + " Present")
            self.label_no_extension.hide()

    def chibi_present(self, present):
        if present:
            chibi = Chibi(self)
            chibi.start()
            self.extensions.append(chibi)
            self.tab_widget.addTab(chibi, 'Chibi')
            self.tab_widget.show()
            self.num_extensions += 1
            self.extension_label.setText(str(self.num_extensions) + " Present")
            self.label_no_extension.hide()

    def start(self):
        if self.firmware_version >= (2, 3, 2):
            async_call(self.master.is_status_led_enabled, None, self.status_led_action.setChecked, self.increase_error_count)

        if self.check_extensions:
            self.check_extensions = False

            self.chibi_present(self.extension_type_preset[self.master.EXTENSION_TYPE_CHIBI])
            self.rs485_present(self.extension_type_preset[self.master.EXTENSION_TYPE_RS485])
            self.wifi_present(self.extension_type_preset[self.master.EXTENSION_TYPE_WIFI])
            self.ethernet_present(self.extension_type_preset[self.master.EXTENSION_TYPE_ETHERNET])
            self.wifi2_present(self.extension_type_preset[self.master.EXTENSION_TYPE_WIFI2])

        self.update_timer.start(1000)

    def stop(self):
        self.update_timer.stop()

    def destroy(self):
        for extension in self.extensions:
            extension.destroy()
            extension.hide()
            extension.setParent(None)

        self.extensions = []

        if self.extension_type:
            self.extension_type.close()

    def is_hardware_version_relevant(self):
        return True

    @staticmethod
    def has_device_identifier(device_identifier):
        return device_identifier == BrickMaster.DEVICE_IDENTIFIER

    def update_data(self):
        async_call(self.master.get_stack_voltage, None, self.get_stack_voltage_async, self.increase_error_count)
        async_call(self.master.get_stack_current, None, self.get_stack_current_async, self.increase_error_count)

        for extension in self.extensions:
            extension.update_data()

    def get_stack_voltage_async(self, voltage):
        self.stack_voltage_label.setText('{:g} V'.format(round(voltage / 1000.0, 1)))

    def get_stack_current_async(self, current):
        self.stack_current_label.setText(format_current(current / 1000.0))

    def extension_clicked(self):
        if self.extension_type is None:
            self.extension_type = ExtensionType(self)

        self.extension_type.show()
